"""App admission uses the real shared contract with synthetic saved evidence."""
import copy
import json
from types import SimpleNamespace

import pytest

from mono import financial_context
from mono.service import MonoService
from mono.verification import verified_result
from test_mono_result_evidence import receipt, saved_receipt, as_bond
from test_mono_publish_store import ready, publication

REAL_VALIDATE_CONTEXT = financial_context.validate_context


@pytest.fixture
def selected(saved_receipt, monkeypatch):
    pytest.importorskip('tools.mono_calc.historical_profile',
        reason='Paired calculator checkout required for real shared-contract integration',
        exc_type=ModuleNotFoundError)
    monkeypatch.setattr(financial_context, 'validate_context', REAL_VALIDATE_CONTEXT)
    from tools.mono_calc import historical_profile as profiles
    from tools.mono_calc import selected_financial_projection as projections
    from tools.mono_calc.contracts import object_hash
    native, record, config, terminal, pins = saved_receipt
    template = 'a' * 64
    monkeypatch.setattr(profiles, 'V9Q_TEMPLATE', template)
    installed = projections._specs(profiles.PROFILE_TEMPLATE)
    monkeypatch.setattr(projections, '_specs', lambda template: installed)
    record['deal_id'] = profiles.AUTHORIZED_DEAL
    record['identity']['template_sha256'] = template
    native['identity']['template_sha256'] = template
    config.template_sha256 = template
    controls = dict(profiles.FORWARD_CONTROLS, AK8=profiles.PROFILE, AK9='2026-09',
                    AK10='2027-08', AK11=profiles.SOURCE_SHA256, AK12='Fixed', AK13=100.0)
    context = dict(metadata_version=2, profile=profiles.PROFILE, comparison_month='2026-09',
        expected_closing_month='2027-08', source_sha256=profiles.SOURCE_SHA256,
        input_sha256='b' * 64, deal_id=record['deal_id'], controls=controls,
        controls_sha256=object_hash(controls))
    trusted = copy.deepcopy(context)
    monkeypatch.setattr(financial_context, 'expected_profile', lambda record, config: copy.deepcopy(trusted))
    native['historical_profile'] = context
    native['selected_financial_projection'] = projections.build_selected_projection(template,
        deal_id=record['deal_id'], historical_profile=context,
        saved_cells={locator: 900001.0 + index for index, (locator, spec) in enumerate(installed.values())})
    as_bond(native, record)
    # All twenty normal monthly financial outputs still need raw evidence.
    for name in ('out_cap_going_in', 'out_yield_on_cost', 'out_loan_close', 'out_debt_service_y1',
                 'out_dscr_y1', 'out_dscr_min', 'out_exit_value', 'out_sources_total', 'out_uses_total'):
        native['outputs'][name] = native['raw_named_outputs'][name] = 17.0
        native['output_metadata'][name] = {'origin': 'Sheet!' + name, 'applicability': {'status': 'applies'}}
    package = __import__('sys').modules['tools.mono_template.package'].inspect(config.template)
    for name in native['outputs']:
        if not any(item['attributes']['name'] == name for item in package['names']):
            package['names'].append({'attributes': {'name': name}, 'text': 'Sheet!' + name})
    terminal.write_text(json.dumps(native), encoding='utf-8')
    return saved_receipt, trusted


def save(native, terminal):
    terminal.write_text(json.dumps(native), encoding='utf-8')


def test_exact_profile_and_selected_historical_value_survive_without_normal_alias(selected):
    (native, record, config, terminal, _), trusted = selected
    result = verified_result(native, record, config, terminal)
    assert result['historical_profile'] == trusted
    assert result['selected_financial_projection'] == native['selected_financial_projection']
    metric = result['selected_financial_projection']['metrics']['historical_net_operating_income_y1']
    assert metric['value'] != result['outputs']['out_noi_y1']
    assert metric['binding_locator'] == 'Historical Bond!F23'
    assert len(result['output_metadata']) == 20
    native['historical_profile']['controls']['AK13'] = 0
    assert result['historical_profile'] == trusted


@pytest.mark.parametrize('attack', ['missing_profile', 'missing_controls', 'wrong_deal', 'forged_controls',
    'wrong_profile', 'wrong_source', 'missing_selected', 'provider_switch', 'metric_changed', 'missing_normal_audit'])
def test_complete_receipt_cannot_promote_with_forged_or_missing_context(selected, attack):
    (native, record, config, terminal, _), _ = selected
    if attack == 'missing_profile': native.pop('historical_profile')
    elif attack == 'missing_controls': native['historical_profile'].pop('controls')
    elif attack == 'wrong_deal': native['historical_profile']['deal_id'] = 'other'
    elif attack == 'forged_controls': native['historical_profile']['controls']['AK14'] = 1
    elif attack == 'wrong_profile': native['historical_profile']['profile'] = 'Forward'
    elif attack == 'wrong_source': native['historical_profile']['source_sha256'] = 'c' * 64
    elif attack == 'missing_selected': native.pop('selected_financial_projection')
    elif attack == 'provider_switch': native['selected_financial_projection']['provider_id'] = 'normal_monthly_v1'
    elif attack == 'metric_changed': native['selected_financial_projection']['metrics']['historical_net_operating_income_y1']['value'] = 17
    elif attack == 'missing_normal_audit': native['raw_named_outputs'].pop('out_noi_y1')
    save(native, terminal)
    with pytest.raises(ValueError):
        verified_result(native, record, config, terminal)


def test_valid_but_changed_prepared_source_rejects_saved_context(selected):
    from tools.mono_calc.contracts import object_hash
    (native, record, config, terminal, _), trusted = selected
    native['historical_profile']['controls']['AK13'] += 1
    native['historical_profile']['controls_sha256'] = object_hash(native['historical_profile']['controls'])
    save(native, terminal)
    with pytest.raises(ValueError, match='current prepared sources'):
        verified_result(native, record, config, terminal)


@pytest.mark.parametrize('address', ['AK' + str(row) for row in range(8, 18)])
def test_each_control_change_is_rejected_even_with_recomputed_caller_hashes(selected, address):
    from tools.mono_calc.contracts import object_hash
    (native, record, config, terminal, _), _ = selected
    context = native['historical_profile']
    value = context['controls'][address]
    context['controls'][address] = value + 1 if type(value) in (int, float) else 'changed'
    context['controls_sha256'] = object_hash(context['controls'])
    projection = native['selected_financial_projection']
    projection['historical_profile'] = copy.deepcopy(context)
    projection['projection_sha256'] = object_hash({key: value for key, value in projection.items() if key != 'projection_sha256'})
    save(native, terminal)
    with pytest.raises(ValueError):
        verified_result(native, record, config, terminal)


def test_package_receipt_cannot_switch_selected_projection(selected):
    from mono.config import digest
    from mono.publication_verification import verify_native_binding
    (native, record, config, terminal, _), _ = selected
    release = financial_context.selection_identity(native)
    release['financial_projection_sha256'] = 'c' * 64
    job = {'_native_receipt': str(terminal), '_native_receipt_sha256': digest(terminal),
           'identity': {'release': release}}
    with pytest.raises(ValueError, match='selected financial provider'):
        verify_native_binding(job, {'cleanup_verified': True})


@pytest.mark.parametrize('attack', ['result_profile', 'result_projection', 'prepared_source'])
def test_profile_only_changes_invalidate_current_result(selected, attack):
    (native, record, config, terminal, _), trusted = selected
    result = verified_result(native, record, config, terminal)
    job = dict(revision=record['revision'], identity=record['identity'], result=result)
    service = MonoService.__new__(MonoService)
    service.config = config
    service.store = SimpleNamespace(current_result=lambda deal: job)
    service.builder = SimpleNamespace(verify=lambda record: None)
    assert service._current_job(record) is job
    if attack == 'result_profile': result['historical_profile']['input_sha256'] = 'c' * 64
    elif attack == 'result_projection': result['selected_financial_projection']['provider_id'] = 'normal_monthly_v1'
    else: trusted['input_sha256'] = 'c' * 64
    assert service._current_job(record) is None


def test_release_identity_tracks_provider_and_projection(selected):
    (native, record, config, terminal, _), trusted = selected
    result = verified_result(native, record, config, terminal)
    identity = financial_context.selection_identity(result)
    assert identity['historical_profile'] == trusted
    result['selected_financial_projection']['projection_sha256'] = 'd' * 64
    assert financial_context.selection_identity(result) != identity
    result['selected_financial_projection']['provider_id'] = 'normal_monthly_v1'
    assert financial_context.selection_identity(result)['financial_provider_id'] != identity['financial_provider_id']


@pytest.mark.parametrize('change', ['provider_id', 'projection_sha256', 'historical_profile'])
def test_package_snapshot_invalidates_when_only_selection_changes(ready, change):
    deals, publications = ready
    original = copy.deepcopy(deals.current_result('fixture')['result'])
    original.update(historical_profile={'profile': 'synthetic historical context'},
        selected_financial_projection={'provider_id': 'esplanade_historical_annual_v1', 'projection_sha256': 'a' * 64})
    def promote(marker, result):
        identity = deals.current('fixture')['identity']
        deals.add_job('fixture', dict(job_id=marker, revision=1, identity=identity, state='queued'))
        deals.update_job('fixture', marker, {'state': 'complete', 'result': result})
        assert deals.promote_result('fixture', marker, 1, identity)
    promote('selected-first', original)
    package = publication(publications)
    altered = copy.deepcopy(original)
    if change == 'historical_profile': altered['historical_profile']['profile'] = 'Forward'
    else: altered['selected_financial_projection'][change] = 'changed'
    promote('selected-next', altered)
    from store.mono_deal_store import MonoConflict
    with pytest.raises(MonoConflict, match='inputs changed'):
        publications.claim('fixture', package, 'stale-selection', 'fixture-request')
