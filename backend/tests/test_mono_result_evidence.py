"""Adversarial checks for calculation evidence at the app boundary."""
import copy
import hashlib
import json
import sys
import time
from pathlib import Path
from types import SimpleNamespace

import pytest

from mono.verification import (
    BOND_RULE, INVESTMENT_OUTPUTS, IRR_OUTPUTS, RETURN_RULE, validate_evidence, verified_result,
)


@pytest.fixture
def receipt():
    names = set(INVESTMENT_OUTPUTS) | {'out_noi_y1', 'out_checks_pass', 'out_checks_error'}
    package = {'names': [{'attributes': {'name': n}, 'text': 'Sheet!' + n} for n in names],
               'sheets': {'Checks': {'constants': {'A' + str(i): {'value': 'check ' + str(i)}
                                                  for i in range(2, 50)}}, 'Sheet': {}}}
    identity = {k: k for k in ('bundle_sha256', 'template_sha256', 'map_sha256', 'code_sha256')}
    identity.update(deal_revision='deal', trusted_rulings_sha256=None, calculation_id='calculation',
                    source_hashes={'source': 'source-hash'})
    record = {'identity': {k: identity[k] for k in ('bundle_sha256', 'template_sha256', 'map_sha256', 'code_sha256')},
              'doc_snapshot': {'assumptions': [{'id': 'deal_type', 'value': 'ACQ'}]}}
    record['identity'].update(deal_sha256='deal', ledger_sha256=None, source_hashes={'source': 'source-hash'})
    raw = {name: 0 for name in names}
    raw['out_checks_pass'] = 'PASS'
    evidence = {name: {'status': 'available', 'value': 0, 'raw_value': 0,
                      'interpretation_rule': RETURN_RULE, 'unwrapped_xirr': 0,
                      'unwrapped_xirr_is_error': False,
                      'cash_flow_audit': {'negative_count': 1, 'positive_count': 1}}
                for name in IRR_OUTPUTS}
    metadata = {name: {'origin': 'Sheet!' + name, 'applicability': {'status': 'applies'}}
                for name in names if not name.startswith('out_checks_')}
    for name, item in evidence.items():
        metadata[name]['availability'] = copy.deepcopy(item)
    native = {'state': 'complete', 'diagnostics': [], 'identity': identity, 'outputs': copy.deepcopy(raw),
              'raw_named_outputs': raw, 'return_evidence': evidence, 'output_metadata': metadata,
              'checks': {'errors': {'Checks': 0, 'Sheet': 0}, 'live_tranches': [True] + [False] * 7,
                         'rows': [{'row': i, 'label': 'check ' + str(i), 'status': 'OK'} for i in range(2, 50)],
                         'investment_returns': {name: 'available' for name in IRR_OUTPUTS}}}
    native.update(cleanup_verified=True, cleanup={
        'policy': 'mono-calculator-cleanup-v1', 'state': 'verified_exit', 'verified': True,
        'native_launched': True, 'native_worker': {'pid': 123, 'returncode': 0},
        'excel_owner': {'pid': 456, 'new_process': True, 'created': 'synthetic-process-identity',
                        'image': 'C:/synthetic/EXCEL.EXE'},
        'observation': {'method': 'identified_process_exit', 'native_worker_exited': True,
                        'owned_excel_present': False}})
    return native, record, package


def test_genuine_zero_survives_with_separate_raw_evidence(receipt):
    native, record, package = receipt
    checks = validate_evidence(native, record, package)
    assert checks['release_passed'] is True
    assert native['outputs']['out_irr_lp'] == 0
    assert 'release_passed' not in native['checks']


def as_bond(native, record):
    record['doc_snapshot']['assumptions'][0]['value'] = 'Bond'
    native['return_evidence'] = {}
    native['checks']['investment_returns'] = {}
    for name in INVESTMENT_OUTPUTS:
        native['outputs'][name] = None
        native['output_metadata'][name].pop('availability', None)
        native['output_metadata'][name]['applicability'] = {
            'status': 'not_applicable', 'rule_id': BOND_RULE, 'reason': 'Bond investment returns do not apply'}


def test_bond_withholds_all_ten_investment_results_but_retains_raw(receipt):
    native, record, package = receipt
    as_bond(native, record)
    assert validate_evidence(native, record, package)['release_passed']
    assert native['raw_named_outputs']['out_irr_lp'] == 0
    assert native['outputs']['out_noi_y1'] == 0


@pytest.mark.parametrize('name', sorted(INVESTMENT_OUTPUTS))
def test_bond_cannot_include_numeric_not_applicable_return(receipt, name):
    native, record, package = receipt
    as_bond(native, record)
    native['outputs'][name] = 0
    with pytest.raises(ValueError, match='Bond investment'):
        validate_evidence(native, record, package)


def test_verified_total_loss_remains_unavailable_as_annualized_rate(receipt):
    native, record, package = receipt
    name = 'out_irr_lp'
    item = native['return_evidence'][name]
    item.update(status='total_loss', value=None, unwrapped_xirr_is_error=True,
                total_return_ratio=-1, display_text='Total loss: \u2212100%',
                reason='Annualized return cannot be calculated without positive receipts.',
                cash_flow_audit={'negative_count': 1, 'positive_count': 0})
    native['outputs'][name] = None
    native['checks']['investment_returns'][name] = 'total_loss'
    native['output_metadata'][name]['availability'] = copy.deepcopy(item)
    assert validate_evidence(native, record, package)['release_passed']


@pytest.mark.parametrize('attack', [
    'raw_missing', 'raw_changed', 'template_changed', 'deal_changed', 'source_changed',
    'sheet_scan_missing', 'sheet_error', 'boolean_error_count', 'check_label', 'check_failure',
    'check_missing', 'aggregate_failure', 'diagnostic', 'state', 'metadata_origin',
    'availability_value', 'availability_status', 'unwrapped_error', 'return_missing',
    'unresolved_route', 'nonfinite', 'financial_na', 'return_check_status',
])
def test_contradictory_or_incomplete_receipt_is_rejected(receipt, attack):
    n, r, package = receipt
    if attack == 'raw_missing': n.pop('raw_named_outputs')
    elif attack == 'raw_changed': n['raw_named_outputs']['out_noi_y1'] = 1
    elif attack == 'template_changed': n['identity']['template_sha256'] = 'wrong'
    elif attack == 'deal_changed': n['identity']['deal_revision'] = 'wrong'
    elif attack == 'source_changed': n['identity']['source_hashes']['source'] = 'wrong'
    elif attack == 'sheet_scan_missing': n['checks']['errors'].pop('Sheet')
    elif attack == 'sheet_error': n['checks']['errors']['Sheet'] = 1
    elif attack == 'boolean_error_count': n['checks']['errors']['Sheet'] = False
    elif attack == 'check_label': n['checks']['rows'][0]['label'] = 'wrong'
    elif attack == 'check_failure': n['checks']['rows'][0]['status'] = 'FAIL'
    elif attack == 'check_missing': n['checks']['rows'].pop()
    elif attack == 'aggregate_failure': n['outputs']['out_checks_pass'] = 'FAIL'
    elif attack == 'diagnostic': n['diagnostics'] = ['Failure']
    elif attack == 'state': n['state'] = 'failed'
    elif attack == 'metadata_origin': n['output_metadata']['out_noi_y1']['origin'] = 'other'
    elif attack == 'availability_value': n['output_metadata']['out_irr_lp']['availability']['value'] = 1
    elif attack == 'availability_status': n['return_evidence']['out_irr_lp']['status'] = 'invalid'
    elif attack == 'unwrapped_error': n['return_evidence']['out_irr_lp']['unwrapped_xirr_is_error'] = True
    elif attack == 'return_missing': n['return_evidence'].pop('out_irr_lp')
    elif attack == 'unresolved_route': r['doc_snapshot']['assumptions'][0]['value'] = None
    elif attack == 'nonfinite': n['outputs']['out_noi_y1'] = float('nan')
    elif attack == 'financial_na': n['output_metadata']['out_noi_y1']['applicability']['status'] = 'not_applicable'
    elif attack == 'return_check_status': n['checks']['investment_returns']['out_irr_lp'] = 'invalid'
    with pytest.raises(ValueError, match='Native evidence rejected'):
        validate_evidence(n, r, package)


def sync_return(native, name='out_irr_lp'):
    item = native['return_evidence'][name]
    native['output_metadata'][name]['availability'] = copy.deepcopy(item)
    native['checks']['investment_returns'][name] = item['status']


@pytest.mark.parametrize('attack', [
    'different_xirr', 'xirr_error', 'infinite_xirr', 'audit_missing', 'audit_null',
    'no_investment', 'no_receipts', 'boolean_investment', 'boolean_receipts',
])
def test_available_return_checks_underlying_economics_after_agreement(receipt, attack):
    native, record, package = receipt
    item = native['return_evidence']['out_irr_lp']
    if attack == 'different_xirr': item['unwrapped_xirr'] = .25
    elif attack == 'xirr_error': item['unwrapped_xirr_is_error'] = True
    elif attack == 'infinite_xirr': item['unwrapped_xirr'] = float('inf')
    elif attack == 'audit_missing': item.pop('cash_flow_audit')
    elif attack == 'audit_null': item['cash_flow_audit'] = None
    elif attack == 'no_investment': item['cash_flow_audit']['negative_count'] = 0
    elif attack == 'no_receipts': item['cash_flow_audit']['positive_count'] = 0
    elif attack == 'boolean_investment': item['cash_flow_audit']['negative_count'] = True
    elif attack == 'boolean_receipts': item['cash_flow_audit']['positive_count'] = True
    sync_return(native)
    with pytest.raises(ValueError, match='available acquisition return lacks a valid underlying calculation'):
        validate_evidence(native, record, package)


@pytest.mark.parametrize('attack', ['positive_receipts', 'numeric_value', 'blank_reason',
                                  'invalid_status', 'boolean_investment', 'boolean_receipts', 'null_audit'])
def test_loss_checks_after_all_evidence_copies_agree(receipt, attack):
    native, record, package = receipt
    item = native['return_evidence']['out_irr_lp']
    item.update(status='total_loss', value=None, unwrapped_xirr_is_error=True,
                total_return_ratio=-1, display_text='Total loss: \u2212100%',
                reason='Annualized return cannot be calculated without positive receipts.',
                cash_flow_audit={'negative_count': 1, 'positive_count': 0})
    native['outputs']['out_irr_lp'] = None
    if attack == 'positive_receipts': item['cash_flow_audit']['positive_count'] = 1
    elif attack == 'numeric_value': item['value'] = native['outputs']['out_irr_lp'] = 0
    elif attack == 'blank_reason': item['reason'] = ' '
    elif attack == 'invalid_status': item['status'] = 'invalid'
    elif attack == 'boolean_investment': item['cash_flow_audit']['negative_count'] = True
    elif attack == 'boolean_receipts': item['cash_flow_audit']['positive_count'] = False
    elif attack == 'null_audit': item['cash_flow_audit'] = None
    sync_return(native)
    with pytest.raises(ValueError, match='invalid acquisition return cannot be released as a loss'):
        validate_evidence(native, record, package)


@pytest.fixture
def saved_receipt(receipt, tmp_path, monkeypatch):
    native, record, package = receipt
    calculations = tmp_path / 'calculations'
    calculations.mkdir()
    (tmp_path / 'bridge').mkdir()
    artifact = calculations / 'disposable-evidence.xlsx'
    artifact.write_bytes(b'Portable artifact identity fixture, not an Excel calculation')
    native['artifact'] = str(artifact)
    native['identity']['workbook_sha256'] = hashlib.sha256(artifact.read_bytes()).hexdigest()
    record.update(revision=1, root=str(tmp_path))
    pin_checks = []
    def load_calculator():
        pin_checks.append('live package checked')
        # This suite exercises orchestration. Shared reconstruction is tested in
        # the calculator's portable suite and the joint native Windows proofs.
        return SimpleNamespace(validate_result_returns=lambda native, route: True,
                               validate_investment_result=lambda native, route: True)
    config = SimpleNamespace(data_root=tmp_path, template=tmp_path / 'not-opened-template.xlsx',
        calculator_root=tmp_path, calculator_python=Path(sys.executable), map_path=tmp_path / 'not-read-map.json',
        capabilities=None, expected_code_sha256='code_sha256',
        load_calculator=load_calculator)
    monkeypatch.setitem(sys.modules, 'tools.mono_template.package', SimpleNamespace(inspect=lambda path: package))
    terminal = tmp_path / 'terminal.json'
    native['investment_evidence'] = {}
    terminal.write_text(json.dumps(native), encoding='utf-8')
    return native, record, config, terminal, pin_checks


def test_verified_result_preserves_raw_and_interpreted_audit_and_reads_live_pins(saved_receipt):
    native, record, config, terminal, pins = saved_receipt
    result = verified_result(native, record, config, terminal)
    assert pins == ['live package checked']
    assert result['raw_named_outputs'] == native['raw_named_outputs']
    assert result['return_evidence'] == native['return_evidence']
    assert result['_native_receipt_sha256'] == hashlib.sha256(terminal.read_bytes()).hexdigest()
    assert result['checks']['return_audits_reconstructed'] is True
    native['return_evidence']['out_irr_lp']['value'] = 5
    assert result['return_evidence']['out_irr_lp']['value'] == 0


@pytest.mark.parametrize('failure',['missing','false','raises'])
def test_verified_result_requires_successful_pinned_shared_audit(saved_receipt,failure):
    native,record,config,terminal,pins=saved_receipt
    def validator(native,route):
        if failure=='raises':
            raise ValueError('Synthetic failed cash-flow reconstruction')
        return False
    config.load_calculator=lambda:SimpleNamespace(**({} if failure=='missing' else {'validate_result_returns':validator}))
    with pytest.raises(ValueError):
        verified_result(native,record,config,terminal)


def test_verified_result_delegates_original_evidence_and_trusted_route_once(saved_receipt):
    native,record,config,terminal,pins=saved_receipt
    calls=[]
    def validator(actual,route):
        calls.append((actual,route))
        return True
    config.load_calculator=lambda:SimpleNamespace(validate_result_returns=validator,
        validate_investment_result=lambda native, route: True)
    result=verified_result(native,record,config,terminal)
    assert calls==[(native,'ACQ')]
    assert result['checks']['return_audits_reconstructed'] is True


@pytest.mark.parametrize('failure', ['missing', 'false', 'raises'])
def test_verified_result_requires_seven_output_shared_audit(saved_receipt, failure):
    native, record, config, terminal, pins = saved_receipt
    def validator(actual, route):
        if failure == 'raises':
            raise ValueError('Synthetic failed seven-output reconstruction')
        return False
    methods = {'validate_result_returns': lambda actual, route: True}
    if failure != 'missing':
        methods['validate_investment_result'] = validator
    config.load_calculator = lambda: SimpleNamespace(**methods)
    with pytest.raises(ValueError):
        verified_result(native, record, config, terminal)


def test_verified_result_preserves_and_delegates_seven_output_evidence(saved_receipt):
    native, record, config, terminal, pins = saved_receipt
    native['investment_evidence'] = {'synthetic': {'marker': 'orchestration fixture'}}
    terminal.write_text(json.dumps(native), encoding='utf-8')
    calls = []
    def validator(actual, route):
        calls.append((actual, route))
        return True
    config.load_calculator = lambda: SimpleNamespace(
        validate_result_returns=lambda actual, route: True,
        validate_investment_result=validator)
    result = verified_result(native, record, config, terminal)
    assert calls == [(native, 'ACQ')]
    assert result['checks']['investment_audits_reconstructed'] is True
    native['investment_evidence']['synthetic']['marker'] = 'changed'
    assert result['investment_evidence']['synthetic']['marker'] == 'orchestration fixture'


@pytest.mark.parametrize('attack', ['outside_root', 'wrong_workbook_hash', 'wrong_receipt_content'])
def test_verified_result_rejects_unbound_artifact_or_receipt(saved_receipt, tmp_path, attack):
    native, record, config, terminal, pins = saved_receipt
    if attack == 'outside_root':
        outside = tmp_path / 'outside.xlsx'
        outside.write_bytes(Path(native['artifact']).read_bytes())
        native['artifact'] = str(outside)
    elif attack == 'wrong_workbook_hash': native['identity']['workbook_sha256'] = 'wrong'
    if attack != 'wrong_receipt_content': terminal.write_text(json.dumps(native), encoding='utf-8')
    else: terminal.write_text('{}', encoding='utf-8')
    expected = {'outside_root': 'outside the private calculation root',
                'wrong_workbook_hash': 'saved workbook identity differs',
                'wrong_receipt_content': 'receipt bytes differ'}[attack]
    with pytest.raises(ValueError, match=expected):
        verified_result(native, record, config, terminal)


def test_receipt_hash_describes_exact_validated_bytes_even_if_path_changes(saved_receipt):
    native, record, config, terminal, pins = saved_receipt
    captured = terminal.read_bytes()
    terminal.write_text('{}', encoding='utf-8')
    result = verified_result(native, record, config, terminal, receipt_bytes=captured)
    assert result['_native_receipt_sha256'] == hashlib.sha256(captured).hexdigest()
    assert result['_native_receipt_sha256'] != hashlib.sha256(terminal.read_bytes()).hexdigest()


def test_current_result_is_invalidated_when_only_receipt_audit_changes(saved_receipt, monkeypatch):
    from mono import service as service_module
    native, record, config, terminal, pins = saved_receipt
    result = verified_result(native, record, config, terminal)
    job = {'revision': record['revision'], 'identity': record['identity'], 'result': result}
    service = service_module.MonoService.__new__(service_module.MonoService)
    service.store = SimpleNamespace(current_result=lambda deal: job)
    service.builder = SimpleNamespace(verify=lambda record: None)
    record['deal_id'] = 'fixture'
    monkeypatch.setattr(service_module, 'read', lambda path: json.loads(Path(path).read_bytes()))
    assert service._current_job(record) is job
    modified = copy.deepcopy(native)
    modified['return_evidence']['out_irr_lp']['cash_flow_audit']['positive_count'] = 0
    terminal.write_text(json.dumps(modified), encoding='utf-8')
    assert service._current_job(record) is None


@pytest.mark.parametrize('reject', [False, True])
def test_provider_stores_complete_verified_evidence_or_fails_without_promotion(saved_receipt, monkeypatch, reject):
    from mono import provider as provider_module
    from store.mono_deal_store import MonoDealStore

    native, record, config, terminal, pins = saved_receipt
    store = MonoDealStore(config.data_root / 'provider.sqlite')
    store.register('fixture', record)
    if reject: native['checks']['errors']['Sheet'] = 1

    class CompletedBridge:
        pid = 987654

        def __init__(self, args, **kwargs):
            (Path(args[-1]) / 'terminal.json').write_text(json.dumps(native), encoding='utf-8')

        def poll(self):
            return 0

    monkeypatch.setattr(provider_module.subprocess, 'Popen', CompletedBridge)
    provider = provider_module.MonoProvider(config, store, SimpleNamespace(verify=lambda record: None))
    try:
        job = provider.submit('fixture', record)
        deadline = time.monotonic() + 5
        while store.job('fixture', job['job_id'])['state'] in ('queued', 'running'):
            assert time.monotonic() < deadline
            time.sleep(.01)
        saved = store.job('fixture', job['job_id'])
        directory = config.data_root / 'bridge' / job['job_id']
        for receipt_name in ('prelaunch.json', 'launch.json', 'bridge-exit.json', 'terminal.json'):
            assert (directory / receipt_name).is_file()
        if reject:
            assert saved['state'] == 'failed'
            assert saved['result'] is None
            assert saved['finished_at']
            assert store.current_result('fixture') is None
        else:
            assert saved['state'] == 'complete'
            result = saved['result']
            assert result['raw_named_outputs'] == native['raw_named_outputs']
            assert result['return_evidence'] == native['return_evidence']
            assert result['_native_receipt_sha256'] == hashlib.sha256((directory / 'terminal.json').read_bytes()).hexdigest()
            assert store.current_result('fixture')['job_id'] == job['job_id']
    finally:
        provider.close()
        provider._thread.join(timeout=5)
