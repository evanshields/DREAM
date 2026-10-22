"""Use the installed calculator's single profile and provider contract."""
from __future__ import annotations

import copy
from pathlib import Path


def expected_profile(record, config):
    from tools.deal_file.core import load_map
    from tools.mono_calc.sources import prepare
    from tools.mono_calc.historical_profile import current_historical
    from tools.mono_template.package import inspect
    from .revisions import read

    root = Path(record['root'])
    bundle = read(root / 'model-inputs/source-bundle.json')
    prepared = prepare(read(root / 'model-inputs/deal-file.json'),
        bundle, root, load_map(config.map_path),
        template_package=inspect(config.template), template_sha256=config.template_sha256,
        trusted_rulings=read(record['trusted_rulings']['path']) if record.get('trusted_rulings') else None)
    if current_historical(config.template_sha256) and any(
            isinstance(region, dict) and region.get('adapter') == 'historical_profile'
            for region in bundle.get('regions', [])):
        # Protected comps admission is checked separately by the deal service.
        # The shared calculator seals this report only after raw historical
        # inputs, normal overlaps and authenticated source intake all validate.
        report = prepared.get('historical_reconciliation') or {}
        intake = report.get('source_intake') or {}
        if (report.get('policy') != 'historical-provider-isolation-v3'
                or intake.get('mode') != 'historical_seller_code_source'):
            raise ValueError('Current financial source preparation is not ready: historical reconciliation is missing')
    return prepared.get('historical_profile')


def validate_context(native, record, config):
    """Bind observed saved context to current trusted source preparation."""
    from tools.mono_calc.historical_profile import validate_metadata
    from tools.mono_calc.selected_financial_projection import validate_selected_projection

    template = record['identity']['template_sha256']
    deal_id = record['deal_id']
    profile = validate_metadata(native.get('historical_profile'), template, deal_id=deal_id)
    if profile is not None and profile != expected_profile(record, config):
        raise ValueError('Saved financial profile differs from the current prepared sources')
    selected = validate_selected_projection(native.get('selected_financial_projection'), template,
        deal_id=deal_id, historical_profile=profile)
    return {'historical_profile': copy.deepcopy(profile),
            'selected_financial_projection': copy.deepcopy(selected)}


def assert_context_copy(receipt, result):
    for key in ('historical_profile', 'selected_financial_projection'):
        if receipt.get(key) != result.get(key):
            raise ValueError('Stored financial context differs from its immutable receipt')


def selection_identity(result):
    """Provider choice and profile remain part of every package freshness check."""
    selected = result.get('selected_financial_projection')
    return {'historical_profile': copy.deepcopy(result.get('historical_profile')),
            'financial_provider_id': selected.get('provider_id') if isinstance(selected, dict) else None,
            'financial_projection_sha256': selected.get('projection_sha256') if isinstance(selected, dict) else None}
