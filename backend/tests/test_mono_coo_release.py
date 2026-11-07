"""Synthetic regressions for the November 7 exact-head COO HOLD."""
import copy
import json
import threading
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

import engine_boundary
from mono import provider as providers
from mono.provider import MonoProvider
from mono.revisions import normalize
from mono.service import MonoService
from test_mono_argon_repairs import calculator, make_world, edit, tree, EVAN, DEAL


@pytest.mark.parametrize('checks', [{}, {'release_passed': False}, {'release_passed': True}])
def test_native_completion_preserves_release_checks(tmp_path, monkeypatch, checks):
    config = SimpleNamespace(data_root=tmp_path, template=tmp_path/'template', map_path=tmp_path/'map',
        calculator_root=tmp_path, calculator_python=Path('unused'), capabilities={}, expected_code_sha256='code')
    (tmp_path/'bridge').mkdir()
    native = {'state':'complete', 'identity':{'calculation_id':'calculation', 'workbook_sha256':'artifact'},
        'outputs':{'out_noi_y1':10}, 'output_metadata':{}, 'checks':checks, 'artifact':'unused'}
    job = {'state':'queued'}
    store = SimpleNamespace(update_job=lambda d,j,changes:job.update(changes), job=lambda *args:job,
        promote_result=lambda *args:None)
    provider = object.__new__(MonoProvider)
    provider.config, provider.store = config, store
    provider.builder = SimpleNamespace(verify=lambda record:None)
    provider._closed = threading.Event()
    provider._quarantine_path = tmp_path/'quarantine'
    def process(*args, **kwargs):
        (tmp_path/'bridge/job/terminal.json').write_text(json.dumps(native),encoding='utf-8')
        return SimpleNamespace(pid=123)
    monkeypatch.setattr(providers.subprocess,'Popen',process)
    monkeypatch.setattr(providers,'wait_for_bridge',lambda *args:False)
    monkeypatch.setattr(providers,'read',lambda p:json.loads(Path(p).read_text()))
    provider._run('deal','job',{'root':str(tmp_path),'identity':{'deal_sha256':'deal','bundle_sha256':'bundle'},'revision':1})
    assert job['result']['checks']==checks


@pytest.mark.parametrize('text',['1,2,3','123,','$1,,2','$,123','$1_000','$1e-5','1,25,000'])
def test_typed_numbers_refuse_malformed_grouping_and_exponents(text):
    with pytest.raises(ValueError): engine_boundary.parse_mono_number(text)


def test_exact_whole_text_does_not_require_float_range(calculator):
    value=normalize({'id':'units','unit':'count'},'1'+'0'*310,'count')
    assert type(value) is int and value==10**310


def test_numeric_whole_values_preserve_integer_type_and_refuse_rounded_floats(calculator):
    entry={'id':'units','unit':'count'}
    assert type(normalize(entry,9007199254740993,'count')) is int
    assert type(normalize(entry,12.0,'count')) is int
    with pytest.raises(ValueError): normalize(entry,9007199254740992.0,'count')


def test_native_scalar_range_refusal_is_a_validation_error(calculator,monkeypatch):
    import tools.mono_calc.adapters as adapters
    monkeypatch.setattr(adapters,'safe_scalar',lambda value:(_ for _ in ()).throw(OverflowError('native range')))
    with pytest.raises(ValueError,match='Unsafe workbook value'):
        normalize({'id':'units','unit':'count'},'1'+'0'*310,'count')


@pytest.mark.parametrize('failure',['schema','copy','identity'])
def test_builder_discards_staging_when_its_own_edit_fails(tmp_path,calculator,monkeypatch,failure):
    config,builder,record=make_world(tmp_path,calculator)
    before=(tree(config.data_root/'revisions'),tree(config.data_root/'trusted'))
    if failure=='schema':
        import tools.deal_file.core as core
        monkeypatch.setattr(core,'validate',lambda doc:['invalid'])
    elif failure=='copy':
        monkeypatch.setattr(builder,'_copy_sources',lambda *args:(_ for _ in ()).throw(OSError('copy refused')))
    else:
        monkeypatch.setattr(builder,'_identity',lambda *args:(_ for _ in ()).throw(ValueError('identity refused')))
        monkeypatch.setattr(builder,'verify',lambda *args:None)
    with pytest.raises((ValueError,OSError)): edit(builder,record)
    assert before==(tree(config.data_root/'revisions'),tree(config.data_root/'trusted'))


@pytest.mark.parametrize('provenance',[{'type':'evan_ruling'},
    {'type':'authenticated_decision','event':{'actor':EVAN}}])
def test_an_earlier_evan_ledger_record_cannot_be_deleted_by_another_actor(tmp_path,calculator,provenance):
    prior={'decision_id':'old','deal_id':DEAL,'assumption_id':'purchase_price','value':100,'provenance':provenance}
    config,builder,record=make_world(tmp_path,calculator,[prior])
    with pytest.raises(PermissionError):
        builder.edit(record,'purchase_price','$250','$','Because',{'issuer':'dream-app','subject':'other'},'request')


@pytest.mark.parametrize('binding',[None,'old','current'])
@pytest.mark.parametrize('valid',[False,True])
def test_view_invalidates_stale_comps_before_go(binding,valid,tmp_path,monkeypatch):
    service=object.__new__(MonoService)
    record={'revision':1,'identity':{'source_hashes':{'comps':'current'}}}
    doc={'assumptions':[],'name':'Fixture'}
    gates={'comps':{'event_id':'comps-event','decision':'confirm','comps_sha256':binding},
        'go_no_go':{'decision':'go','result_id':'result','comps_event_id':'comps-event'}}
    service.config=SimpleNamespace(map_path=tmp_path/'map',registrations={'fixture':{}})
    service.store=SimpleNamespace(revisions=lambda *a:[{'doc_snapshot':doc}],gates=lambda *a:copy.deepcopy(gates),jobs=lambda *a:[])
    monkeypatch.setattr(service,'_record',lambda *a:record)
    monkeypatch.setattr(service,'_current_job',lambda *a:{'job_id':'job','result':{'result_id':'result'}})
    if valid: monkeypatch.setattr(service,'_prepared',lambda *a:(doc,{},[],{'ready':True,'problems':[],'applicability':{}}))
    else:
        monkeypatch.setattr(service,'_prepared',lambda *a:(_ for _ in ()).throw(ValueError('stale')))
        record.update(doc_snapshot=doc,bundle_snapshot={})
        import sys
        from types import ModuleType
        core=ModuleType('tools.deal_file.core'); core.load_map=lambda path:[]
        monkeypatch.setitem(sys.modules,'tools.deal_file.core',core)
    result=service.view('fixture',{})
    if valid and binding=='current': assert result['gates']['comps'] is not None
    else:
        assert result['gates']['comps'] is None
        assert result['gates']['go_no_go'] is None
