"""Validate native evidence before the app stores a releasable result."""
from __future__ import annotations

import copy
import hashlib
import json
import math
from pathlib import Path

from .config import digest
from .cleanup import verified_cleanup


INVESTMENT_OUTPUTS = frozenset({
    'out_irr_gross', 'out_irr_lp', 'out_irr_gp', 'out_em_gross',
    'out_em_lp', 'out_em_gp', 'out_coc_avg', 'out_promote_gp',
    'out_equity_lp', 'out_equity_gp',
})
IRR_OUTPUTS = frozenset({'out_irr_gross', 'out_irr_lp', 'out_irr_gp'})
BOND_RULE = 'evan_bond_no_investment_returns_2026_10_20'
RETURN_RULE = 'evan_acquisition_total_loss_2026_10_20'


def _require(condition, message):
    if not condition:
        raise ValueError('Native evidence rejected: ' + message)


def _finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _count(value, *, positive=False):
    return type(value) is int and value >= (1 if positive else 0)


def validate_evidence(native, record, package):
    """Check receipt content against the pinned template and submitted revision.

    This validates evidence and does not calculate financial outputs. Files and
    configuration pins are checked separately by verified_result.
    """
    _require(isinstance(native, dict), 'receipt is malformed')
    _require(verified_cleanup(native), 'positive native cleanup evidence is absent')
    _require(native.get('state') == 'complete' and native.get('diagnostics') == [],
             'receipt is not a successful completed calculation')
    identity = native.get('identity', {})
    _require(isinstance(identity, dict), 'receipt identity is malformed')
    expected = record['identity']
    for source_key, target_key in (
        ('deal_sha256', 'deal_revision'), ('bundle_sha256', 'bundle_sha256'),
        ('template_sha256', 'template_sha256'), ('map_sha256', 'map_sha256'),
        ('code_sha256', 'code_sha256'), ('ledger_sha256', 'trusted_rulings_sha256'),
    ):
        _require(source_key in expected and target_key in identity
                 and expected[source_key] == identity[target_key], 'revision or package identity differs')
    _require(isinstance(identity.get('calculation_id'), str) and bool(identity['calculation_id']),
             'calculation identity is absent')
    direct_comps = any(s.get('id') == 'comps' for s in record.get('bundle_snapshot', {}).get('sources', []))
    sources = {k: v for k, v in expected.get('source_hashes', {}).items() if k != 'comps' or direct_comps}
    _require(identity.get('source_hashes') == sources, 'source identities differ')
    names = {n['attributes']['name'] for n in package['names']
             if n['attributes']['name'].startswith('out_')}
    financial = {name for name in names if not name.startswith('out_checks_')}
    values, raw, metadata = (native.get(k) for k in ('outputs', 'raw_named_outputs', 'output_metadata'))
    _require(all(isinstance(v, dict) for v in (values, raw, metadata)),
             'outputs, raw audit values or metadata are absent')
    _require(set(values) == names and set(raw) == names and set(metadata) == financial,
             'output coverage differs from the pinned template')
    for key in ('out_checks_pass', 'out_checks_error'):
        _require(values.get(key) == raw.get(key), 'aggregate raw checks disagree')
    _require(values.get('out_checks_pass') == 'PASS' and _finite(values.get('out_checks_error'))
             and values['out_checks_error'] == 0, 'aggregate checks failed')
    checks = native.get('checks', {})
    _require(isinstance(checks, dict), 'checks are malformed')
    errors = checks.get('errors')
    _require(isinstance(errors, dict) and set(errors) == set(package['sheets'])
             and all(_finite(v) and v == 0 for v in errors.values()),
             'complete all-sheet zero-error scan is absent')
    rows = checks.get('rows')
    _require(isinstance(rows, list) and len(rows) == 48, 'check rows are incomplete')
    for row, entry in zip(range(2, 50), rows):
        _require(isinstance(entry, dict), 'check row is malformed')
        label = package['sheets']['Checks']['constants']['A' + str(row)]['value']
        status = entry.get('status')
        _require(entry.get('row') == row and entry.get('label') == label,
                 'check row identity differs')
        _require(isinstance(status, str) and (status in ('OK', 'n/a') or status.startswith('CAUTION')),
                 'a check row failed or is unresolved')
    live = checks.get('live_tranches')
    _require(isinstance(live, list) and len(live) == 8
             and all(isinstance(v, (bool, int, float)) and v in (0, 1) for v in live),
             'live-tranche vector is malformed')
    route_values = [a.get('value') for a in record['doc_snapshot']['assumptions'] if a.get('id') == 'deal_type']
    _require(len(route_values) == 1 and route_values[0] in ('ACQ', 'Bond', 'ACQ then Bond'),
             'deal route is unresolved')
    bond = route_values[0] == 'Bond'
    evidence = native.get('return_evidence')
    _require(isinstance(evidence, dict) and set(evidence) == (set() if bond else IRR_OUTPUTS),
             'investment return audit coverage is incomplete')
    _require(all(isinstance(v, dict) for v in evidence.values()), 'return evidence is malformed')
    _require(checks.get('investment_returns') == {k: v.get('status') for k, v in evidence.items()},
             'return check statuses disagree with their evidence')
    origins = {n['attributes']['name']: n['text'] for n in package['names'] if n['attributes']['name'] in financial}
    for name in financial:
        meta = metadata[name]
        _require(isinstance(meta, dict), 'output metadata is malformed')
        _require(meta.get('origin') == origins[name], 'named output origin differs')
        rule = meta.get('applicability', {})
        _require(isinstance(rule, dict), 'output applicability is malformed')
        if bond and name in INVESTMENT_OUTPUTS:
            _require(rule.get('status') == 'not_applicable' and rule.get('rule_id') == BOND_RULE
                     and isinstance(rule.get('reason'), str) and bool(rule['reason'].strip())
                     and values[name] is None, 'Bond investment return is not consistently withheld')
            continue
        _require(rule.get('status') == 'applies', 'financial output applicability is contradictory')
        if name not in IRR_OUTPUTS:
            _require(_finite(values[name]) and values[name] == raw[name], 'financial raw value differs')
            continue
        item = evidence[name]
        _require(item.get('interpretation_rule') == RETURN_RULE and item.get('raw_value') == raw[name]
                 and item.get('value') == values[name] and meta.get('availability') == item,
                 'return interpretation is detached from its raw evidence')
        if item.get('status') == 'available':
            audit = item.get('cash_flow_audit')
            _require(_finite(values[name]) and item.get('unwrapped_xirr_is_error') is False
                     and _finite(item.get('unwrapped_xirr')) and values[name] == raw[name]
                     and math.isclose(values[name], item['unwrapped_xirr'], rel_tol=1e-10, abs_tol=1e-10)
                     and isinstance(audit, dict)
                     and _count(audit.get('negative_count'), positive=True)
                     and _count(audit.get('positive_count'), positive=True),
                     'available acquisition return lacks a valid underlying calculation')
        else:
            audit = item.get('cash_flow_audit', {})
            _require(item.get('status') == 'total_loss' and values[name] is None
                     and item.get('unwrapped_xirr_is_error') is True
                     and item.get('total_return_ratio') == -1
                     and item.get('display_text') == 'Total loss: \u2212100%'
                     and isinstance(item.get('reason'), str) and bool(item['reason'].strip())
                     and isinstance(audit, dict)
                     and _count(audit.get('negative_count'), positive=True)
                     and type(audit.get('positive_count')) is int and audit['positive_count'] == 0,
                     'invalid acquisition return cannot be released as a loss')
    return dict(copy.deepcopy(checks), release_passed=True, cleanup_verified=True)


def verified_result(native, record, config, terminal_path, *, receipt_bytes=None, expected_comps_binding=None):
    from tools.mono_template.package import inspect

    # Load and hash the actual installed package rather than comparing a pin to itself.
    calculator = config.load_calculator()
    if receipt_bytes is None:
        receipt_bytes = Path(terminal_path).read_bytes()
    _require(json.loads(receipt_bytes) == native, 'receipt bytes differ from the validated content')
    from .financial_context import validate_context
    financial_context = validate_context(native, record, config)
    from .comps_admission import canonical_packet
    canonical = canonical_packet(record)
    if canonical is not None:
        _require(expected_comps_binding is not None and native.get('comps_binding') == expected_comps_binding,
                 'protected comps binding differs from dispatched export')
        _require(native.get('identity', {}).get('trusted_comps_sha256') == expected_comps_binding['trusted_comps_sha256'],
                 'protected comps transport identity differs')
    else:
        _require(native.get('comps_binding') is None, 'unexpected canonical comps binding')
    checks = validate_evidence(native, record, inspect(config.template))
    from engine_boundary import verify_mono_return_audits, verify_mono_investment_audits
    route = next(a['value'] for a in record['doc_snapshot']['assumptions'] if a['id'] == 'deal_type')
    verify_mono_return_audits(calculator, native, route)
    checks['return_audits_reconstructed'] = True
    verify_mono_investment_audits(calculator, native, route)
    checks['investment_audits_reconstructed'] = True
    artifact = Path(native['artifact']).resolve(strict=True)
    _require(artifact.is_relative_to((config.data_root / 'calculations').resolve(strict=True)),
             'workbook is outside the private calculation root')
    _require(digest(artifact) == native['identity'].get('workbook_sha256'), 'saved workbook identity differs')
    return {**financial_context, 'result_id': native['identity']['calculation_id'], 'outputs': copy.deepcopy(native['outputs']),
            'output_metadata': copy.deepcopy(native['output_metadata']), 'checks': checks,
            'artifact_sha256': native['identity']['workbook_sha256'], 'identity': copy.deepcopy(native['identity']),
            'artifact_limitations': copy.deepcopy(native.get('artifact_limitations', [])),
            'raw_named_outputs': copy.deepcopy(native['raw_named_outputs']),
            'return_evidence': copy.deepcopy(native['return_evidence']),
            'investment_evidence': copy.deepcopy(native['investment_evidence']),
            **({'comps_binding': copy.deepcopy(expected_comps_binding)} if expected_comps_binding else {}),
            '_cleanup': copy.deepcopy(native['cleanup']),
            '_native_receipt': str(terminal_path),
            '_native_receipt_sha256': hashlib.sha256(receipt_bytes).hexdigest(),
            '_artifact': str(artifact)}
