"""Slice 1 of the evidence viewer plan: the pure evidence contract validator.

SYNTHETIC fixtures only. No real deal file is read. The validator is pure: no file, network,
database or model access, and no Decimal (value comparison is text only)."""
import copy
import json
import os

import pytest

from evidence import contract as c

_FIX = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "fixtures", "evidence", "synthetic_oak_court_contract.json")


@pytest.fixture()
def fx():
    with open(_FIX, encoding="utf-8") as fh:
        return json.load(fh)


def _codes(result):
    return [e["code"] for e in result["errors"]]


def test_fixture_is_marked_synthetic(fx):
    assert fx["marker"] == "SYNTHETIC"
    assert "SYNTHETIC" in fx["cell"]["evidence"]["citations"][0]["line_text"]


def test_fixture_page_count_agrees_with_expected_page(fx):
    doc = fx["document"]
    cite = fx["cell"]["evidence"]["citations"][0]
    assert doc["page_count"] == 5
    assert doc["expected_page"] == 4
    assert 1 <= doc["expected_page"] <= doc["page_count"]
    assert cite["page"] == doc["expected_page"]


def test_state_list_is_closed_and_reuses_run_status_vocabulary():
    assert c.STATES == ("ok", "missing", "hash_mismatch", "unverified", "unreadable",
                        "invalid", "ambiguous", "conflict", "no_source")
    assert c.BASES == ("document", "llm_inferred", "policy_default", "manual_entry", "none")


def test_clean_cell_is_valid(fx):
    cell = fx["cell"]
    result = c.validate_evidence(cell["evidence"], cell["value"],
                                 page_count=fx["document"]["page_count"])
    assert result == {"valid": True, "state": "ok", "errors": []}


def test_unknown_basis_is_invalid(fx):
    ev = copy.deepcopy(fx["cell"]["evidence"])
    ev["basis"] = "vibes"
    result = c.validate_evidence(ev, 41250000)
    assert result["valid"] is False and result["state"] == "invalid"
    assert "unknown_basis" in _codes(result)


def test_wrong_schema_is_invalid(fx):
    ev = copy.deepcopy(fx["cell"]["evidence"])
    ev["schema"] = "dream.evidence.v0"
    assert "bad_schema" in _codes(c.validate_evidence(ev, 41250000))


def test_document_with_no_citations_is_invalid(fx):
    ev = copy.deepcopy(fx["cell"]["evidence"])
    ev["citations"] = []
    assert "document_needs_citation" in _codes(c.validate_evidence(ev, 41250000))


@pytest.mark.parametrize("basis", ["llm_inferred", "policy_default", "manual_entry", "none"])
def test_non_document_with_citations_is_invalid(fx, basis):
    ev = copy.deepcopy(fx["cell"]["evidence"])
    ev["basis"] = basis
    ev["reason"] = "because"
    assert "citations_not_allowed" in _codes(c.validate_evidence(ev, 41250000))


@pytest.mark.parametrize("basis", ["llm_inferred", "policy_default", "manual_entry", "none"])
def test_non_document_needs_reason(basis):
    ev = {"schema": "dream.evidence.v1", "basis": basis, "citations": []}
    assert "reason_required" in _codes(c.validate_evidence(ev, 1))
    ev["reason"] = "typed by a person"
    assert c.validate_evidence(ev, 1)["valid"] is True


def test_engine_input_fixture_evidence_is_valid(fx):
    ei = fx["engine_input"]
    assert c.validate_evidence(ei["evidence"], ei["value"])["valid"] is True


def test_matched_text_must_normalise_to_value(fx):
    ev = copy.deepcopy(fx["cell"]["evidence"])
    assert "matched_text_mismatch" in _codes(c.validate_evidence(ev, 41250001))


@pytest.mark.parametrize("matched,value,ok", [
    ("$41,250,000", 41250000, True),
    ("41 250 000", 41250000, True),
    ("$41,250,000.00", 41250000, True),
    ("6.5%", 0.065, True),
    ("65%", 0.65, True),
    ("6.5%", 6.5, False),
    ("$1,000", 10000, False),
    ("abc", 1, False),
])
def test_normalise_compares_as_text(matched, value, ok):
    assert c.matched_text_agrees(matched, value) is ok


def test_booleans_and_none_never_agree():
    assert c.matched_text_agrees("1", True) is False
    assert c.matched_text_agrees("1", None) is False


def test_page_is_one_based_and_within_page_count(fx):
    base = fx["cell"]["evidence"]
    for page, ok in [(0, False), (-1, False), (1, True), (5, True), (6, False)]:
        ev = copy.deepcopy(base)
        ev["citations"][0]["page"] = page
        result = c.validate_evidence(ev, 41250000, page_count=5)
        assert result["valid"] is ok, page
        if not ok:
            assert "bad_page" in _codes(result)


def test_rects_must_be_well_formed(fx):
    for bad in ([], [[1, 2, 3]], [[10, 10, 5, 20]], [["a", 1, 2, 3]], "x"):
        ev = copy.deepcopy(fx["cell"]["evidence"])
        ev["citations"][0]["rects_pt"] = bad
        assert "bad_rects" in _codes(c.validate_evidence(ev, 41250000)), bad


def test_rects_must_sit_inside_the_page(fx):
    ev = copy.deepcopy(fx["cell"]["evidence"])
    ev["citations"][0]["rects_pt"] = [[72.0, 310.5, 900.0, 324.1]]
    assert "bad_rects" in _codes(c.validate_evidence(ev, 41250000))


def test_doc_sha256_must_be_64_lower_hex(fx):
    for bad in ("abc", "G" * 64, "A" * 64, 5):
        ev = copy.deepcopy(fx["cell"]["evidence"])
        ev["citations"][0]["doc_sha256"] = bad
        assert "bad_sha256" in _codes(c.validate_evidence(ev, 41250000)), bad


def test_missing_citation_field_is_invalid(fx):
    ev = copy.deepcopy(fx["cell"]["evidence"])
    del ev["citations"][0]["line_text"]
    assert "missing_field" in _codes(c.validate_evidence(ev, 41250000))


def test_xlsx_citation_uses_sheet_and_cell_ref(fx):
    ev = copy.deepcopy(fx["cell"]["evidence"])
    cite = ev["citations"][0]
    for k in ("page", "page_width_pt", "page_height_pt", "rects_pt"):
        del cite[k]
    cite.update({"doc_kind": "xlsx", "sheet": "Rent Roll", "cell_ref": "D7"})
    assert c.validate_evidence(ev, 41250000)["valid"] is True
    cite["cell_ref"] = "7D"
    assert "bad_cell_ref" in _codes(c.validate_evidence(ev, 41250000))


def test_unknown_doc_kind_is_invalid(fx):
    ev = copy.deepcopy(fx["cell"]["evidence"])
    ev["citations"][0]["doc_kind"] = "docx"
    assert "bad_doc_kind" in _codes(c.validate_evidence(ev, 41250000))


def test_conflicting_citations_give_conflict_state(fx):
    ev = copy.deepcopy(fx["cell"]["evidence"])
    second = copy.deepcopy(ev["citations"][0])
    second["matched_text"] = "$40,000,000"
    second["page"] = 2
    ev["citations"].append(second)
    result = c.validate_evidence(ev, 41250000)
    assert result["state"] == "conflict"
    assert result["valid"] is False
    assert "conflict" in _codes(result)


def test_non_dict_evidence_is_invalid():
    for bad in (None, [], "x", 3):
        result = c.validate_evidence(bad, 1)
        assert result["valid"] is False and result["state"] == "invalid"


def test_validator_does_not_mutate_input(fx):
    ev = fx["cell"]["evidence"]
    before = copy.deepcopy(ev)
    c.validate_evidence(ev, 41250000, page_count=5)
    assert ev == before


# Engine-input key identifiers (plan section 1: "cell:B10", "engine:stabilized_noi").
@pytest.mark.parametrize("ident,expected", [
    ("cell:B10", ("cell", "B10")),
    ("cell:AA145", ("cell", "AA145")),
    ("engine:stabilized_noi", ("engine_input", "stabilized_noi")),
])
def test_identifier_parses(ident, expected):
    assert c.parse_identifier(ident) == expected


@pytest.mark.parametrize("bad", ["B10", "cell:", "cell:10B", "cell:b10", "engine:", "engine:Stab NOI",
                                 "engine:1abc", "irr", "tab:B10", "", None, 5, "cell:B10:x"])
def test_identifier_rejects_bad(bad):
    with pytest.raises(ValueError):
        c.parse_identifier(bad)


def test_identifier_round_trips():
    assert c.format_identifier("cell", "B10") == "cell:B10"
    assert c.format_identifier("engine_input", "stabilized_noi") == "engine:stabilized_noi"
    with pytest.raises(ValueError):
        c.format_identifier("metric", "irr")


def test_engine_input_evidence_map_validates(fx):
    ei = fx["engine_input"]
    inputs = {ei["key"]: ei["value"], "exit_cap": 0.0525}
    evidence_map = {ei["key"]: ei["evidence"]}
    results = c.validate_engine_input_evidence(inputs, evidence_map)
    assert results[ei["key"]]["valid"] is True
    # A key with no evidence entry is no_source with the plan's reason.
    assert results["exit_cap"] == {"valid": True, "state": "no_source",
                                   "errors": [], "reason": "no source recorded"}


def test_engine_input_evidence_for_unknown_key_is_invalid(fx):
    ei = fx["engine_input"]
    results = c.validate_engine_input_evidence({"exit_cap": 0.05}, {"ghost_key": ei["evidence"]})
    assert results["ghost_key"]["state"] == "invalid"
    assert "unknown_engine_key" in [e["code"] for e in results["ghost_key"]["errors"]]


def test_module_is_pure_no_forbidden_imports():
    src = open(c.__file__, encoding="utf-8").read()
    for banned in ("import decimal", "from decimal", "sqlite3", "psycopg", "import requests",
                   "import httpx", "openai", "import fitz", "import os", "open("):
        assert banned not in src, banned


# ---- Red team repair group 1: one percent normalization family for value and matched text ----
@pytest.mark.parametrize("matched,value,ok", [
    ("6.5%", "6.5%", True),
    ("6.5%", "0.065", True),
    ("0.065", "6.5%", True),
    ("65%", "65%", True),
    ("6.5", "6.5%", False),
    ("6.5%", "6.5", False),
    ("$1,000", "1,000", True),
    ("6.5%%", "0.065", False),
    ("6.5%", "6.5%%", False),
    ("%6.5%", "0.065", False),
    ("6%5%", "0.65", False),
])
def test_percent_in_value_text_is_scaled_like_matched_text(matched, value, ok):
    assert c.matched_text_agrees(matched, value) is ok


# ---- Group 2: infinite page dimensions must not disable the upper bound ----
@pytest.mark.parametrize("field", ["page_width_pt", "page_height_pt"])
@pytest.mark.parametrize("bad", [float("inf"), float("-inf"), float("nan")])
def test_non_finite_page_dimension_is_rejected(fx, field, bad):
    ev = copy.deepcopy(fx["cell"]["evidence"])
    ev["citations"][0][field] = bad
    ev["citations"][0]["rects_pt"] = [[72.0, 310.5, 100.0, 324.1]]  # in bounds on its own
    assert "bad_rects" in _codes(c.validate_evidence(ev, 41250000))


@pytest.mark.parametrize("idx", [0, 1, 2, 3])
@pytest.mark.parametrize("bad", [float("inf"), float("-inf"), float("nan")])
def test_non_finite_rect_coordinate_is_rejected(fx, idx, bad):
    ev = copy.deepcopy(fx["cell"]["evidence"])
    rect = [72.0, 310.5, 100.0, 324.1]
    rect[idx] = bad
    ev["citations"][0]["rects_pt"] = [rect]
    assert "bad_rects" in _codes(c.validate_evidence(ev, 41250000))


@pytest.mark.parametrize("second", ["", "   ", "N/A"])
def test_unparseable_second_matched_text_is_invalid_not_conflict(fx, second):
    ev = copy.deepcopy(fx["cell"]["evidence"])
    other = copy.deepcopy(ev["citations"][0])
    other["matched_text"] = second
    ev["citations"].append(other)
    result = c.validate_evidence(ev, 41250000)
    assert result["state"] == "invalid"
    assert "conflict" not in _codes(result)


# ---- Group 3: citation field types and nonempty semantic text ----
_TEXT_FIELDS = ["doc_name", "line_text", "matched_text", "label_text", "locator", "locator_version"]


@pytest.mark.parametrize("field", _TEXT_FIELDS)
@pytest.mark.parametrize("bad", [5, None, ["x"], {"a": 1}, True])
def test_citation_text_field_must_be_a_string(fx, field, bad):
    ev = copy.deepcopy(fx["cell"]["evidence"])
    ev["citations"][0][field] = bad
    result = c.validate_evidence(ev, 41250000)
    assert result["valid"] is False
    assert "bad_field_type" in _codes(result)


@pytest.mark.parametrize("field", _TEXT_FIELDS)
@pytest.mark.parametrize("bad", ["", "   ", "\t\n"])
def test_citation_text_field_must_be_nonempty(fx, field, bad):
    ev = copy.deepcopy(fx["cell"]["evidence"])
    ev["citations"][0][field] = bad
    result = c.validate_evidence(ev, 41250000)
    assert result["valid"] is False
    assert "empty_field" in _codes(result)


@pytest.mark.parametrize("bad,code", [("", "empty_field"), (7, "bad_field_type")])
def test_xlsx_sheet_must_be_a_nonempty_string(fx, bad, code):
    ev = copy.deepcopy(fx["cell"]["evidence"])
    cite = ev["citations"][0]
    for k in ("page", "page_width_pt", "page_height_pt", "rects_pt"):
        del cite[k]
    cite.update({"doc_kind": "xlsx", "sheet": bad, "cell_ref": "D7"})
    assert code in _codes(c.validate_evidence(ev, 41250000))


def test_mixed_valid_and_invalid_citations_still_report_invalid(fx):
    ev = copy.deepcopy(fx["cell"]["evidence"])
    bad = copy.deepcopy(ev["citations"][0])
    bad["locator"] = ""
    ev["citations"].append(bad)
    result = c.validate_evidence(ev, 41250000)
    assert result["valid"] is False and result["state"] == "invalid"
    assert any(e["message"].startswith("citation 1 ") for e in result["errors"])
    assert not any(e["message"].startswith("citation 0 ") for e in result["errors"])


# ---- Group 4: malformed roots are refused, never coerced to a no-source state ----
@pytest.mark.parametrize("bad", [None, [], "x", 3, ("a",)])
def test_non_dict_engine_inputs_are_refused(bad):
    with pytest.raises(ValueError):
        c.validate_engine_input_evidence(bad, {})


@pytest.mark.parametrize("bad", [None, [], "x", 3, ("a",)])
def test_non_dict_evidence_map_is_refused(bad):
    with pytest.raises(ValueError):
        c.validate_engine_input_evidence({"exit_cap": 0.05}, bad)


def test_empty_dicts_are_still_accepted():
    assert c.validate_engine_input_evidence({}, {}) == {}
