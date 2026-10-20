"""Ambiguous rates and absent fields must not become silent financial changes."""
from decimal import Decimal

import pytest

from mono.revisions import rate_input, edit_prefill, assumption_for_edit


@pytest.mark.parametrize('entered', ['1', '0.01', 1, 0.01, True, '', 'NaN%', 'inf%', '1e999999999%'])
def test_rate_entry_requires_explicit_scale_and_finite_value(entered):
    with pytest.raises(ValueError):
        rate_input(entered)


@pytest.mark.parametrize('entered,expected', [('1%', .01), ('0%', 0), ('-5%', -.05),
    ('200%', 2), ('ratio:0.01', .01), ('ratio:0', 0)])
def test_explicit_rate_scale_is_preserved_without_blanket_clipping(entered, expected):
    assert rate_input(entered) == expected


def test_rate_prefill_roundtrips_and_does_not_show_stored_ratio_as_percent():
    for value in [.01, 0, -.05, 2, .0525, .0333333333333]:
        text = edit_prefill(value, '%')
        assert text.endswith('%')
        assert Decimal(str(rate_input(text))) == Decimal(str(value))
    assert edit_prefill(None, '%') == ''
    assert edit_prefill(0, '$') == '0'


def test_missing_mapped_field_starts_as_explicit_absence_without_policy_default():
    doc = {'assumptions': []}
    entry = {'id': 'fee', 'label': 'Fee', 'unit': '%', 'mono_cell': 'Inputs!B4', 'policy_default': .01}
    field = assumption_for_edit(doc, entry)
    assert field is doc['assumptions'][0]
    assert field['value'] is None
    assert field['unit'] == '%'
    assert field['mono_cell'] == 'Inputs!B4'
    assert 'absent' in field['note'].lower()
    assert 'policy_default' not in field


def test_existing_null_and_its_history_are_not_replaced_by_missing_seed():
    field = {'id': 'fee', 'value': None, 'note': 'Original missing evidence', 'source': {'type': 'evan_override'}}
    doc = {'assumptions': [field]}
    assert assumption_for_edit(doc, {'id': 'fee'}) is field
    assert field['note'] == 'Original missing evidence'
    assert len(doc['assumptions']) == 1
