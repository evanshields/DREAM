"""Adversarial checks for calculation evidence at the app boundary."""
import copy

import pytest

from mono.verification import (
    BOND_RULE, INVESTMENT_OUTPUTS, IRR_OUTPUTS, RETURN_RULE, validate_evidence,
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
