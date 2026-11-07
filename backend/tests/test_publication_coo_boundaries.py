"""Invented source/receipt counterexamples for the November 7 review."""
import copy
import json
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest
from fastapi import HTTPException

from mono import financial_context
from mono.publication_files import PublicationFilesError, verify_package
from mono.service import MonoService
from store.mono_deal_store import MonoConflict
from test_mono_publish_store import ready, publication, finish
from test_mono_publication_diagnostics import failed_job, GENERIC
from test_mono_publication_files import fixture, repack, save
from test_mono_comps_integration import canonical


@pytest.mark.parametrize('bad',[1,'false',{'error':'failed'}])
def test_snapshot_requires_literal_release_true(ready,monkeypatch,bad):
    deals,store=ready
    original=deals._job
    def job(*args):
        result=copy.deepcopy(original(*args)); result['result']['checks']['release_passed']=bad
        return result
    monkeypatch.setattr(deals,'_job',job)
    with pytest.raises(MonoConflict): store.snapshot('fixture')


@pytest.mark.parametrize('bad',['x','g'*64,'A'*64])
def test_snapshot_requires_an_actual_sha256_digest(ready,monkeypatch,bad):
    deals,store=ready
    original=deals._job
    def job(*args):
        result=copy.deepcopy(original(*args)); result['result']['artifact_sha256']=bad
        return result
    monkeypatch.setattr(deals,'_job',job)
    with pytest.raises(MonoConflict): store.snapshot('fixture')


@pytest.mark.parametrize('kind',['memo','onepager','deck','workbook'])
def test_complete_rejects_unvalidated_deliverable_entries(ready,kind):
    _,store=ready
    job,_=store.claim('fixture',publication(store),'coo','coo')
    package={'identity':job['identity'],'validation':{'passed':True},
        'deliverables':{k:{'files':[{'path':k+'/test','sha256':'a'*64}],
                             'validation':{'status':'passed'}} for k in ['memo','onepager','deck','workbook']}}
    package['deliverables'][kind]={'fixture':True}
    with pytest.raises(MonoConflict): store.update('fixture',job['job_id'],{'state':'complete','package':package})


def test_absent_profile_cannot_bypass_current_expected_context(monkeypatch):
    def module(name,**attrs):
        item=ModuleType(name); item.__dict__.update(attrs); monkeypatch.setitem(sys.modules,name,item)
    module('tools'); module('tools.mono_calc')
    module('tools.mono_calc.historical_profile',validate_metadata=lambda *a,**k:None)
    module('tools.mono_calc.selected_financial_projection',validate_selected_projection=lambda *a,**k:None)
    monkeypatch.setattr(financial_context,'expected_profile',lambda *a:{'profile':'required-current-context'})
    with pytest.raises(ValueError,match='profile differs'):
        financial_context.validate_context({}, {'deal_id':'invented','identity':{'template_sha256':'a'*64}}, object())


@pytest.mark.parametrize('ready_flag,binding',[(False,'c'*64),(True,None),(True,'d'*64)])
def test_calculate_checks_source_readiness_and_current_comps_before_dispatch(monkeypatch,ready_flag,binding):
    import engine_boundary
    service=object.__new__(MonoService)
    record={'revision':1,'identity':{'source_hashes':{'comps':'c'*64}}}
    service.provider=object()
    service.store=SimpleNamespace(idempotent_result=lambda *a:None)
    monkeypatch.setattr(service,'_record',lambda *a:record)
    monkeypatch.setattr(service,'_expected',lambda *a:None)
    monkeypatch.setattr(service,'view',lambda *a:{'readiness':{'ready':ready_flag},
        'gates':{'comps':None if binding is None else {'decision':'confirm','comps_sha256':binding}}})
    submitted=[]
    monkeypatch.setattr(engine_boundary,'submit_mono_calculation',lambda *a,**k:submitted.append(a) or {})
    with pytest.raises(HTTPException) as exc:
        service.calculate('invented',{'idempotency_key':'key'}, {})
    assert exc.value.status_code==409 and submitted==[]


@pytest.mark.parametrize('error',[PublicationFilesError('C:/private/seller.xlsx'),MonoConflict('C:/private/source.json')])
def test_curated_error_classes_do_not_make_arbitrary_messages_public(ready,tmp_path,error):
    job=failed_job(ready,tmp_path,error)
    assert job['diagnostics']==[type(error).__name__+': '+GENERIC]


def test_workbook_proof_must_cover_the_saved_workbook_sheets(tmp_path):
    root=tmp_path/'package'
    record=fixture(root)
    proof_path=root/'verification.json'
    proof=json.loads(proof_path.read_text())
    proof['all_sheet_errors']={'an-unrelated-sheet':0}
    save(proof_path,proof)
    from mono.config import digest
    next(e for e in record['files'] if e['path']=='verification.json')['sha256']=digest(proof_path)
    record['workbook_verification']['sha256']=digest(proof_path)
    repack(root,record)
    with pytest.raises(PublicationFilesError,match='sheet'):
        verify_package(root,identity=record['identity'],projection_sha256=record['projection_sha256'])


@pytest.mark.parametrize('link',[
    '[source]: C:/Users/private/proof.xml',
    '<a href="C:/Users/private/proof.xml">proof</a>',
    '<file:///C:/private/proof.xml>',
    r'[proof](\\server\share\proof.xml)',
    '[proof](../../../../private/proof.xml)',
])
def test_phase_doc_check_rejects_nonportable_link_forms(tmp_path,monkeypatch,link):
    import test_phase4_docs_links as links
    path=tmp_path/'phase.md'; path.write_text(link,encoding='utf-8')
    monkeypatch.setattr(links,'PHASE_DOCS',[path])
    with pytest.raises(AssertionError): links.test_no_phase_document_links_to_a_machine_only_path()


@pytest.mark.parametrize('packet',[{},[],{'format':'another-format'}])
def test_direct_json_comps_cannot_silently_skip_canonical_admission(canonical,packet):
    from test_mono_comps_integration import raw, sha
    from mono.comps_admission import canonical_packet
    c=canonical
    packet_bytes=raw(packet)
    (Path(c.record['root'])/'model-inputs/comps.json').write_bytes(packet_bytes)
    c.record['bundle_snapshot']['sources'][0]['sha256']=sha(packet_bytes)
    bundle_bytes=raw(c.record['bundle_snapshot'])
    (Path(c.record['root'])/'model-inputs/source-bundle.json').write_bytes(bundle_bytes)
    c.record['identity']['bundle_sha256']=sha(bundle_bytes)
    c.record['identity']['source_hashes']['comps']=sha(packet_bytes)
    with pytest.raises(ValueError,match='canonical comps packet|JSON object artifact'): canonical_packet(c.record)
