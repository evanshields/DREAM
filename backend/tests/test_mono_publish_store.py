"""Publication identity and race proofs with explicit engineering records."""
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest

from store.mono_deal_store import MonoConflict, MonoDealStore, MonoNotFound
from store.mono_publish_store import MonoPublicationStore


def revision(number=1):
    return {'revision': number, 'identity': {'deal_sha256': str(number), 'source_hashes': {'comps': 'comp-source'}}}


def gate(deals, kind, decision, event_id):
    return deals.record_gate('fixture', 1, {'event_id': event_id, 'revision': 1,
        'gate': kind, 'decision': decision, 'identity': revision()['identity'],
        'comps_sha256': 'comp-source', 'result_id': 'native-result',
        'comps_event_id': 'comps-1'}, event_id, event_id)


@pytest.fixture
def ready(tmp_path):
    deals = MonoDealStore(tmp_path / 'mono.sqlite')
    deals.register('fixture', revision())
    deals.register('other', revision())
    calc = {'job_id': 'calc', 'revision': 1, 'identity': revision()['identity'], 'state': 'queued'}
    deals.add_job('fixture', calc)
    deals.update_job('fixture', 'calc', {'state': 'complete', 'result': {'result_id': 'native-result',
        'artifact_sha256': 'w' * 64, 'identity': {'calculation_id': 'native-result'},
        'checks': {'release_passed': True}}})
    assert deals.promote_result('fixture', 'calc', 1, revision()['identity'])
    gate(deals, 'comps', 'confirm', 'comps-1')
    gate(deals, 'go_no_go', 'go', 'go-1')
    return deals, MonoPublicationStore(deals)


def publication(store, job_id='publish-1'):
    return {'job_id': job_id, 'deal_id': 'fixture', 'revision': 1, 'state': 'queued',
        'identity': {'release': store.snapshot('fixture'), 'renderer_sha256': 'a' * 64,
                     'projection_sha256': 'b' * 64, 'asset_policy_sha256': 'c' * 64,
                     'narrative_sha256': 'd' * 64}}


def finish(store, job):
    return store.update('fixture', job['job_id'], {'state': 'complete', 'package': {
        'identity': job['identity'], 'validation': {'passed': True},
        'deliverables': {k: {'fixture': True} for k in ['memo', 'onepager', 'deck', 'workbook']}}})


def test_two_instances_create_one_actor_payload_bound_job_and_restart_replay(ready):
    deals, store = ready
    barrier = Barrier(2)

    def submit(marker):
        independent = MonoPublicationStore(MonoDealStore(deals.path))
        draft = publication(independent, marker)
        barrier.wait()
        return independent.claim('fixture', draft, 'same-key', 'same-actor-and-payload')

    with ThreadPoolExecutor(max_workers=2) as pool:
        responses = list(pool.map(submit, ['first', 'second']))
    assert sum(created for _, created in responses) == 1
    assert responses[0][0]['job_id'] == responses[1][0]['job_id']
    original = responses[0][0]
    deals.commit_revision('fixture', 1, revision(2), {'fixture': True}, 'edit', 'edit')
    reopened = MonoPublicationStore(MonoDealStore(deals.path))
    assert reopened.claim('fixture', original, 'same-key', 'same-actor-and-payload') == (original, False)
    with pytest.raises(MonoConflict):
        reopened.claim('fixture', original, 'same-key', 'different-actor-or-payload')
    assert len(reopened.jobs('fixture')) == 1


def test_revision_during_render_keeps_completed_package_historical(ready):
    deals, store = ready
    job, _ = store.claim('fixture', publication(store), 'publish', 'actor-request')
    deals.commit_revision('fixture', 1, revision(2), {'fixture': True}, 'edit', 'edit')
    finish(store, job)
    assert not store.promote('fixture', job['job_id'])
    assert store.current('fixture') is None
    assert store.job('fixture', job['job_id'])['state'] == 'complete'


@pytest.mark.parametrize('changed', ['go', 'comps'])
def test_changed_human_gate_invalidates_current_package_and_late_promotion(ready, changed):
    deals, store = ready
    job, _ = store.claim('fixture', publication(store), 'publish', 'actor-request')
    finish(store, job)
    assert store.promote('fixture', job['job_id'])
    assert store.current('fixture')['job_id'] == job['job_id']
    if changed == 'go':
        gate(deals, 'go_no_go', 'no_go', 'go-withdrawn')
    else:
        gate(deals, 'comps', 'confirm', 'comps-2')
    assert store.current('fixture') is None
    assert not store.promote('fixture', job['job_id'])
    with pytest.raises(MonoConflict):
        store.snapshot('fixture')


def test_partial_failed_or_cancelled_output_cannot_be_promoted(ready):
    _, store = ready
    job, _ = store.claim('fixture', publication(store), 'publish', 'actor-request')
    with pytest.raises(MonoConflict, match='four'):
        store.update('fixture', job['job_id'], {'state': 'complete', 'package': {
            'identity': job['identity'], 'validation': {'passed': True}, 'deliverables': {'memo': {}}}})
    assert store.job('fixture', job['job_id'])['state'] == 'queued'
    store.update('fixture', job['job_id'], {'cancel_requested': True})
    with pytest.raises(MonoConflict, match='Cancelled'):
        finish(store, job)
    store.update('fixture', job['job_id'], {'state': 'cancelled', 'package': None})
    assert not store.promote('fixture', job['job_id'])
    with pytest.raises(MonoConflict, match='immutable'):
        store.update('fixture', job['job_id'], {'state': 'running'})


def test_scope_and_identity_are_enforced_and_restart_never_resubmits(ready):
    deals, store = ready
    job, _ = store.claim('fixture', publication(store), 'publish', 'actor-request')
    with pytest.raises(MonoNotFound):
        store.job('other', job['job_id'])
    with pytest.raises(MonoConflict):
        store.update('fixture', job['job_id'], {'identity': {}})
    assert store.recover_interrupted() == [job['job_id']]
    assert store.recover_interrupted() == []
    assert store.job('fixture', job['job_id'])['package'] is None
    assert not store.promote('fixture', job['job_id'])
    assert MonoPublicationStore(MonoDealStore(deals.path)).job('fixture', job['job_id'])['state'] == 'interrupted'


def test_queued_plan_hash_is_distinct_from_the_compiled_projection_hash(ready):
    _,store=ready
    job=publication(store)
    job['identity']={'release':store.snapshot('fixture'),'renderer_sha256':'a'*64,'source_plan_sha256':'e'*64}
    actual,_=store.claim('fixture',job,'plan','actor-request')
    assert actual['identity']==job['identity'] and 'projection_sha256' not in actual['identity']
    with pytest.raises(MonoConflict,match='actual projection'):
        finish(store,job)
    package={'identity':job['identity'],'validation':{'passed':True},'projection_sha256':'f'*64,
        'deliverables':{kind:{'synthetic':True} for kind in ('memo','onepager','deck','workbook')}}
    store.update('fixture',job['job_id'],{'state':'complete','package':package})
    assert store.promote('fixture',job['job_id'])


def test_plan_request_cannot_relabel_its_hash_as_a_compiled_projection(ready):
    _,store=ready
    job=publication(store)
    job['identity']['source_plan_sha256']='e'*64
    with pytest.raises(MonoConflict,match='not an already compiled'):
        store.claim('fixture',job,'ambiguous','actor-request')
