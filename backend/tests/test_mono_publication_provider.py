"""A publisher retains ownership through uncertain cleanup and durable cancellation."""
import copy
from threading import Event
import time
from types import SimpleNamespace

import pytest

import mono.publication as publication_module
from mono.provider import wait_for_bridge
from store.mono_deal_store import MonoConflict
from test_mono_publish_store import ready


def inputs(ready, tmp_path):
    deals, publications = ready
    result = copy.deepcopy(deals.current_result('fixture')['result'])
    result.update(_artifact=str(tmp_path/'not-opened.xlsx'), _native_receipt=str(tmp_path/'not-read.json'))
    deals.add_job('fixture', {'job_id':'calc-private', 'revision':1,
        'identity':deals.current('fixture')['identity'], 'state':'queued'})
    deals.update_job('fixture','calc-private', {'state':'complete','result':result})
    assert deals.promote_result('fixture','calc-private',1,deals.current('fixture')['identity'])
    config = SimpleNamespace(data_root=tmp_path, calculator_root=tmp_path,
        calculator_python=tmp_path/'not-executed', expected_code_sha256='synthetic')
    builder = SimpleNamespace(verify=lambda record:None)
    registration = {'projection':'synthetic-only','artifact_root':str(tmp_path),
        'projection_sha256':'b'*64, 'renderer_sha256':'a'*64}
    plan = {'identity':{'deal_id':'fixture','asset_policy_sha256':'c'*64,'narrative_sha256':'d'*64}}
    return publications, config, builder, registration, plan


def test_hung_publisher_retains_lease_and_shared_restart_quarantine(ready,tmp_path,monkeypatch):
    store, config, builder, registration, plan = inputs(ready,tmp_path)
    stop = Event()

    class HungProcess:
        pid = 987654

        def poll(self):
            return 0 if stop.is_set() else None

        def terminate(self):
            pytest.fail('A native owner must not be killed after an observation timeout')

    monkeypatch.setattr(publication_module,'registered_plan',lambda *args:plan)
    monkeypatch.setattr(publication_module.subprocess,'Popen',lambda *args,**kwargs:HungProcess())
    monkeypatch.setattr(publication_module,'wait_for_bridge',lambda process,directory,closing,quarantine:
        wait_for_bridge(process,directory,closing,quarantine,timeout=0,cancel_grace=0))
    provider = publication_module.PublicationProvider(config,store,builder)
    record = store.deals.current('fixture')
    release = store.snapshot('fixture')
    try:
        job = provider.submit('fixture',record,registration,release,plan,key='publish',request_digest='actor-request')
        deadline = time.monotonic()+5
        while store.job('fixture',job['job_id'])['state']!='failed':
            assert time.monotonic()<deadline
            time.sleep(.01)
        assert (tmp_path/'dispatcher-quarantine.json').is_file()
        assert provider._thread.is_alive() and not provider._lease.closed
        with pytest.raises(MonoConflict,match='cleanup'):
            provider.submit('fixture',record,registration,release,plan,key='again',request_digest='again')
        with pytest.raises(RuntimeError,match='owns'):
            publication_module.PublicationProvider(config,store,builder)
    finally:
        provider.close()
        stop.set()
        provider._thread.join(timeout=5)
    assert not provider._thread.is_alive() and provider._lease.closed
    restarted = publication_module.PublicationProvider(config,store,builder)
    try:
        with pytest.raises(MonoConflict,match='cleanup'):
            restarted.submit('fixture',record,registration,release,plan,key='restart',request_digest='restart')
        assert store.job('fixture',job['job_id'])['state']=='failed'
    finally:
        restarted.close()
        restarted._thread.join(timeout=5)


def test_queued_cancellation_does_not_launch_or_open_native_resources(ready,tmp_path,monkeypatch):
    from test_mono_publish_store import publication
    store, config, builder, _, _ = inputs(ready,tmp_path)
    job = publication(store)
    job['identity']['release'] = store.snapshot('fixture')
    store.claim('fixture',job,'cancel-first','request')
    provider = publication_module.PublicationProvider.__new__(publication_module.PublicationProvider)
    provider.config, provider.store, provider.builder = config,store,builder
    provider._quarantine_path = tmp_path/'dispatcher-quarantine.json'
    provider._quarantine_path.write_text('Synthetic unverified cleanup',encoding='utf-8')
    monkeypatch.setattr(publication_module.subprocess,'Popen',lambda *a,**k:pytest.fail('Cancelled job must not dispatch'))
    provider.cancel('fixture',job['job_id'])
    provider._run('fixture',job['job_id'])
    assert store.job('fixture',job['job_id'])['state']=='cancelled'


@pytest.mark.parametrize('change',['none','revision','withdraw_review','cancel','last_instant_cancel','uncertain_cleanup'])
def test_completed_synthetic_worker_promotes_only_current_uncancelled_package(ready,tmp_path,monkeypatch,change):
    """Exercise the real queue, file verifier and store with a fake document worker."""
    import json
    import shutil
    from mono.config import canonical_hash, digest
    from test_mono_publication_files import fixture as package_fixture, repack, save
    from test_mono_publish_store import revision, gate
    monkeypatch.setattr('mono.revisions.read',lambda path:json.loads(Path(path).read_text(encoding='utf-8')))
    store, config, builder, registration, _ = inputs(ready,tmp_path)
    source = tmp_path/'synthetic-package'
    receipt = package_fixture(source)
    receipt['identity'].update(deal_id='fixture',asset_policy_sha256='c'*64,narrative_sha256='d'*64)
    projection = {'identity':receipt['identity'],'synthetic_boundary_only':True}
    save(source/'projection.json',projection)
    save(source/'verification.json',{'policy':'mono-publication-extraction-v1',
        'identity':receipt['identity'],'all_sheet_errors':{'synthetic':0}})
    for entry in receipt['files']:
        if entry['path'] in ('projection.json','verification.json'):
            entry['sha256']=digest(source/entry['path'])
    receipt['workbook_verification']['sha256']=digest(source/'verification.json')
    receipt['projection_sha256']=canonical_hash(projection)
    registration['projection_sha256']=receipt['projection_sha256']
    repack(source,receipt)
    monkeypatch.setattr(publication_module,'registered_plan',lambda *args:projection)
    complete_attempted = []
    original_update = store.update

    def racing_update(deal_id,job_id,changes):
        if change=='last_instant_cancel' and changes.get('state')=='complete' and not complete_attempted:
            complete_attempted.append(True)
            provider.cancel(deal_id,job_id)
        return original_update(deal_id,job_id,changes)

    monkeypatch.setattr(store,'update',racing_update)

    def finished_process(command,**kwargs):
        directory = Path(command[-1])
        shutil.copytree(source,directory/'package')
        copied = json.loads((directory/'package/package.json').read_text())
        copied['workbook_verification']['path']=str(directory/'package/verification.json')
        save(directory/'package/package.json',copied)
        save(directory/'terminal.json',{**copied,'cleanup_verified':change!='uncertain_cleanup'})
        if change=='revision':
            store.deals.commit_revision('fixture',1,revision(2),{'synthetic':True},'edit','edit')
        elif change=='withdraw_review':
            gate(store.deals,'go_no_go','no_go','withdrawn')
        elif change=='cancel':
            provider.cancel('fixture',directory.name)
        return SimpleNamespace(pid=987654,poll=lambda:0)

    from pathlib import Path
    monkeypatch.setattr(publication_module.subprocess,'Popen',finished_process)
    provider = publication_module.PublicationProvider(config,store,builder)
    try:
        job = provider.submit('fixture',store.deals.current('fixture'),registration,store.snapshot('fixture'),
            projection,key='publish',request_digest='request')
        deadline = time.monotonic()+5
        while store.job('fixture',job['job_id'])['state'] in ('queued','running'):
            assert time.monotonic()<deadline
            time.sleep(.01)
        actual = store.job('fixture',job['job_id'])
        expected = 'failed' if change=='uncertain_cleanup' else 'cancelled' if 'cancel' in change else 'complete'
        assert actual['state']==expected, actual['diagnostics']
        current = store.current('fixture')
        assert (current is not None)==(change=='none')
        if current:
            assert current['job_id']==job['job_id']
        if 'cancel' in change:
            assert actual['package'] is None
        if change=='uncertain_cleanup':
            assert (tmp_path/'dispatcher-quarantine.json').is_file() and actual['package'] is None
    finally:
        provider.close()
        provider._thread.join(timeout=5)
    assert not provider._thread.is_alive()
