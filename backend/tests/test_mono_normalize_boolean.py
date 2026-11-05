"""A Boolean never becomes a number or a workbook choice.

Python treats True as 1 and False as 0, so every numeric and choice check must refuse a Boolean first.
The calculator helpers are stubbed because they live in the paired private checkout.
"""
import sys
from types import ModuleType

import pytest

from mono.revisions import normalize


@pytest.fixture(autouse=True)
def calculator_helpers(monkeypatch):
    for name in ('tools', 'tools.deal_file', 'tools.mono_calc'):
        monkeypatch.setitem(sys.modules, name, ModuleType(name))
    readiness = ModuleType('tools.deal_file.readiness')
    readiness._text_id = lambda identifier: False
    adapters = ModuleType('tools.mono_calc.adapters')
    adapters.safe_scalar = lambda value: True
    monkeypatch.setitem(sys.modules, 'tools.deal_file.readiness', readiness)
    monkeypatch.setitem(sys.modules, 'tools.mono_calc.adapters', adapters)


NUMBER = {'id': 'units', 'unit': 'count'}
CHOICE = {'id': 'switch', 'unit': '', 'dropdown': [0, 1]}


@pytest.mark.parametrize('entered', [True, False])
def test_boolean_is_refused_for_a_number(entered):
    with pytest.raises(ValueError, match='Boolean'):
        normalize(NUMBER, entered, 'count')


@pytest.mark.parametrize('entered', [True, False])
def test_boolean_is_refused_for_a_workbook_choice_even_when_zero_and_one_are_choices(entered):
    with pytest.raises(ValueError, match='Boolean'):
        normalize(CHOICE, entered, '')


def test_plain_numbers_and_choices_still_pass():
    assert normalize(NUMBER, 12, 'count') == 12
    assert normalize(CHOICE, 1, '') == 1
    assert normalize(CHOICE, '0', '') == 0
