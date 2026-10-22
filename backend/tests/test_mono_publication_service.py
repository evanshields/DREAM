"""Authenticated orchestration counterexamples, not financial acceptance proofs."""
from pathlib import Path
from types import SimpleNamespace

from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
import pytest

from mono.config import canonical_hash
from mono.publication_service import PublicationService
from routers.mono import create_router
from store.mono_deal_store import MonoConflict
from test_mono_publish_store import ready, revision, gate
from test_mono_publication_files import fixture as package_fixture


ACTOR = {'issuer':'synthetic', 'subject':'owner'}
BODY = {'expected_revision':1, 'expected_deal_sha256':'1', 'idempotency_key':'publish-request'}


@pytest.fixture
def setup(ready, tmp_path, monkeypatch):
    deals, _ = ready
    config = SimpleNamespace(data_root=tmp_path, registrations={'fixture':{'publication':{'synthetic':True}}})
    mono = SimpleNamespace(config=config, store=deals, builder=SimpleNamespace(verify=lambda record:None))

    def record(deal_id, actor):
        if actor.get('subject') not in ('owner','associated-peer'):
            raise HTTPException(403, 'No configured association')
        if deal_id not in config.registrations:
            raise HTTPException(404, 'Deal is not registered')
        return deals.current(deal_id)

    def expected(record, body):
        if (body['expected_revision'] != record['revision']
                or body['expected_deal_sha256'] != record['identity']['deal_sha256']):
            raise HTTPException(409, 'Revision changed')

    def conflict(error):
        raise HTTPException(409, str(error))

    mono._record, mono._expected, mono._conflict = record, expected, conflict
    mono._prepared = lambda record:({}, {}, {}, {'ready':True})
    mono._current_job = lambda record:deals.current_result(record['deal_id'])
    service = PublicationService(mono, start_provider=False)
    plan = {'identity':{'deal_id':'fixture','asset_policy_sha256':'c'*64,'narrative_sha256':'d'*64}}
    monkeypatch.setattr('mono.publication_service.registered_plan', lambda *args:plan)
    count = []

    class SyntheticProvider:
        _quarantine_path = tmp_path/'not-created'

        def submit(self, deal_id, record, registration, release, projection, *, key, request_digest):
            job = {'job_id':'publication-'+str(len(count)), 'deal_id':deal_id, 'revision':record['revision'],
                'identity':{'release':release, 'renderer_sha256':'a'*64, 'projection_sha256':'b'*64,
                    'asset_policy_sha256':'c'*64, 'narrative_sha256':'d'*64},
                'state':'queued', 'diagnostics':[], 'steps':[], '_private_secret':'never public',
                '_revision_record':record, '_registration':registration}
            if getattr(self, 'package_receipt', None):
                job['_publication_identity']=self.package_receipt['identity']
                job['identity']['projection_sha256']=self.package_receipt['projection_sha256']
                job['_native_receipt'] = str(tmp_path/'native-receipt.json')
                from mono.config import digest
                job['_native_receipt_sha256'] = digest(job['_native_receipt'])
            actual, created = service.store.claim(deal_id, job, key, request_digest)
            count.append(created)
            return actual

        def cancel(self, deal_id, job_id):
            service.store.update(deal_id, job_id, {'cancel_requested':True})

    service.provider = SyntheticProvider()
    mono.publications = service
    app = FastAPI()
    app.include_router(create_router(mono, lambda:ACTOR), prefix='/api/deals')
    return service, mono, count, TestClient(app)


def test_actor_payload_replay_survives_later_revision_and_never_dispatches_again(setup):
    service, mono, calls, _ = setup
    first = service.submit('fixture', BODY, ACTOR)
    assert '_private_secret' not in first and first['state']=='queued'
    mono.store.commit_revision('fixture', 1, revision(2), {'synthetic':True}, 'edit', 'edit')
    assert service.submit('fixture', BODY, ACTOR)['job_id']==first['job_id']
    assert calls==[True]
    with pytest.raises(HTTPException) as denied:
        service.submit('fixture', BODY, {**ACTOR,'subject':'associated-peer'})
    assert denied.value.status_code==409 and calls==[True]


def test_authentication_and_missing_reviews_prevent_any_dispatch(setup):
    service, mono, calls, _ = setup
    with pytest.raises(HTTPException) as denied:
        service.submit('fixture', BODY, {'subject':'outsider'})
    assert denied.value.status_code==403 and calls==[]
    gate(mono.store, 'go_no_go', 'no_go', 'withdrawn')
    with pytest.raises(HTTPException) as blocked:
        service.submit('fixture', BODY, ACTOR)
    assert blocked.value.status_code==409 and calls==[]


def test_source_plan_from_another_deal_cannot_appear_publishable_or_dispatch(setup, monkeypatch):
    service, mono, calls, _ = setup
    mono.config.registrations['fixture']['publication'] = {'source_plan':'synthetic-v2-plan'}
    monkeypatch.setattr('mono.publication_service.registered_plan',
                        lambda *args: {'deal_id':'different-deal','variants':{'ACQ':{}}})
    state = service.state('fixture', ACTOR)
    assert state['can_publish'] is False
    assert any('different deal' in reason for reason in state['blocking_reasons'])
    with pytest.raises(HTTPException) as blocked:
        service.submit('fixture', BODY, ACTOR)
    assert blocked.value.status_code == 409
    assert calls == []


def complete(setup):
    service, mono, _, _ = setup
    job_id = 'publication-0'
    root = mono.config.data_root/'publications'/job_id/'package'
    root.parent.mkdir(parents=True)
    receipt = package_fixture(root)
    from mono.config import digest
    from test_mono_publication_files import save, repack
    import json
    native = mono.config.data_root/'native-receipt.json'
    native.write_text('{"synthetic_native_receipt":true}', encoding='utf-8')
    proof_path = root/'verification.json'
    proof = json.loads(proof_path.read_text())
    proof['receipt_sha256'] = digest(native)
    save(proof_path, proof)
    for entry in receipt['files']:
        if entry['path'] == 'verification.json':
            entry['sha256'] = digest(proof_path)
    receipt['workbook_verification']['sha256'] = digest(proof_path)
    repack(root, receipt)
    service.provider.package_receipt = receipt
    public = service.submit('fixture', BODY, ACTOR)
    assert public['job_id']==job_id
    job = service.store.job('fixture',job_id)
    package = {'identity':job['identity'],'validation':{'passed':True},
        'deliverables':receipt['deliverables'],'_root':str(root),'_receipt':receipt}
    service.store.update('fixture', job_id, {'state':'complete','package':package})
    assert service.store.promote('fixture',job_id)
    return job_id, root


def test_complete_files_download_only_through_current_scoped_package(setup):
    service, mono, _, _ = setup
    job_id, root = complete(setup)
    assert service.state('fixture', ACTOR)['current']['job_id']==job_id
    response = service.download('fixture', job_id, 'memo', 'pdf', ACTOR)
    assert Path(response.path)==root/'memo/source.pdf'
    assert response.headers['cache-control']=='private, no-store'
    mono.store.commit_revision('fixture', 1, revision(2), {'synthetic':True}, 'edit', 'edit')
    assert service.state('fixture', ACTOR)['current'] is None
    assert service.job('fixture',job_id,ACTOR)['state']=='complete'
    with pytest.raises(HTTPException) as historical:
        service.download('fixture',job_id,'memo','pdf',ACTOR)
    assert historical.value.status_code==409


@pytest.mark.parametrize('kind,variant', [('workbook', 'workbook'), ('package', 'archive')])
def test_historical_download_filename_preserves_comparison_month(tmp_path, monkeypatch, kind, variant):
    service = PublicationService.__new__(PublicationService)
    service.mono = SimpleNamespace(_record=lambda *args: None)
    job = {'state': 'complete', 'package': {'verified': True}, 'identity': {'release': {
        'financial_provider_id': 'esplanade_historical_annual_v1',
        'historical_profile': {'comparison_month': '2026-09', 'expected_closing_month': '2027-08'}}}}
    service.store = SimpleNamespace(job=lambda *args: job)
    service._verified = lambda *args, **kwargs: (tmp_path, {'verified': True})
    suffix = '.xlsx' if kind == 'workbook' else '.zip'
    path = tmp_path / ('verified-file' + suffix)
    monkeypatch.setattr('mono.publication_service.download_entry',
        lambda *args: {'path': path.name, 'media_type': 'application/octet-stream'})
    monkeypatch.setattr('mono.publication_service.output_file', lambda *args: path)
    response = service.download('esplanade', 'publication', kind, variant, ACTOR)
    assert response.filename.startswith('historical-source-comparison-2026-09-')
    assert response.filename.endswith(suffix)
    assert '2027-08' not in response.filename


@pytest.mark.parametrize('change', ['native_receipt', 'reopened_binding', 'missing_cleanup', 'null_cleanup'])
def test_later_fixed_package_use_rechecks_native_binding_and_positive_cleanup(setup, change):
    from mono.config import digest
    from test_mono_publication_files import save, repack
    import json
    service, mono, _, _ = setup
    job_id, root = complete(setup)
    assert service.state('fixture', ACTOR)['current'] is not None
    receipt = json.loads((root/'package.json').read_text())
    if change == 'native_receipt':
        (mono.config.data_root/'native-receipt.json').write_text('{"substituted":true}', encoding='utf-8')
    elif change == 'reopened_binding':
        proof_path = root/'verification.json'
        proof = json.loads(proof_path.read_text())
        proof['receipt_sha256'] = '0'*64
        save(proof_path, proof)
        for entry in receipt['files']:
            if entry['path'] == 'verification.json':
                entry['sha256'] = digest(proof_path)
        receipt['workbook_verification']['sha256'] = digest(proof_path)
        repack(root, receipt)
    else:
        if change == 'missing_cleanup':
            receipt.pop('cleanup_verified')
        else:
            receipt['cleanup_verified'] = None
        save(root/'package.json', receipt)
    assert service.state('fixture', ACTOR)['current'] is None
    with pytest.raises(HTTPException) as denied:
        service.download('fixture', job_id, 'memo', 'pdf', ACTOR)
    assert denied.value.status_code == 409


def test_changed_output_and_withdrawn_review_invalidate_current_download(setup):
    service, mono, _, _ = setup
    job_id, root = complete(setup)
    (root/'memo/source.pdf').write_bytes(b'changed')
    assert service.state('fixture', ACTOR)['current'] is None
    assert service.state('fixture', ACTOR)['can_publish'] is True
    with pytest.raises(HTTPException) as changed:
        service.download('fixture',job_id,'memo','pdf',ACTOR)
    assert changed.value.status_code==409
    gate(mono.store, 'go_no_go', 'no_go', 'withdrawn')
    assert service.state('fixture', ACTOR)['can_publish'] is False


def test_cross_deal_scope_and_private_fields_do_not_leak(setup):
    service, mono, _, _ = setup
    job = service.submit('fixture', BODY, ACTOR)
    mono.config.registrations['other']={'publication':{'synthetic':True}}
    with pytest.raises(HTTPException) as absent:
        service.job('other',job['job_id'],ACTOR)
    assert absent.value.status_code==404
    serialized = str(service.state('fixture',ACTOR))
    assert 'never public' not in serialized and '_registration' not in serialized


@pytest.mark.parametrize('injection',[{'path':'C:/private'}, {'actor':{'subject':'owner'}},
    {'projection':{}},{'renderer_sha256':'a'*64}])
def test_http_publish_rejects_caller_paths_actors_or_renderer_configuration(setup,injection):
    _, _, calls, client = setup
    response = client.post('/api/deals/fixture/mono/publications',json={**BODY,**injection})
    assert response.status_code==422 and calls==[]


def test_http_publication_state_submit_and_cancel_use_authenticated_service(setup):
    _, _, calls, client = setup
    assert client.get('/api/deals/fixture/mono/publications').status_code==200
    result = client.post('/api/deals/fixture/mono/publications',json=BODY)
    assert result.status_code==200 and calls==[True]
    job_id = result.json()['job_id']
    assert client.get('/api/deals/fixture/mono/publications/'+job_id).status_code==200
    result = client.post('/api/deals/fixture/mono/publications/'+job_id+'/cancel',json={})
    assert result.status_code==200 and result.json()['cancel_requested'] is True
