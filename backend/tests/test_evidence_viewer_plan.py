"""Consistency checks on the evidence viewer plan (docs/plans/2026-11-03-app-evidence-viewer.md).

The plan is a document, not code. These checks keep its contract, its locator,
its storage tables and its save path from contradicting each other.
"""
import re
import unittest
from pathlib import Path

PLAN = Path(__file__).resolve().parents[2] / "docs" / "plans" / "2026-11-03-app-evidence-viewer.md"
TEXT = PLAN.read_text(encoding="utf-8").replace("\r\n", "\n")


def section(start, end):
    i = TEXT.index(start)
    return TEXT[i:TEXT.index(end, i)]


CONTRACT = section("### 1. Data contract", "### 2. Document store")
STORE = section("### 2. Document store", "### 3. Locator")
LOCATOR = section("### 3. Locator", "### 4. Backend endpoints")
FRONT = section("### 5. Front-end component", "### 6. Test plan")
TESTS = section("### 6. Test plan", "### 7. Risks")
SLICES = section("### 8. Slice order", "### 9. Open questions")


class NormalisationTests(unittest.TestCase):
    def test_unit_is_a_closed_set_that_fixes_the_percent_scale(self):
        self.assertRegex(CONTRACT, r"`unit` is a closed set")
        for name in ("currency", "ratio", "pct_points"):
            self.assertIn("`%s`" % name, CONTRACT)
        self.assertIn('"unit"', CONTRACT)

    def test_normalisation_names_trailing_zeros_negatives_and_unsupported_formats(self):
        rule = re.search(r"- `matched_text` must normalise.*", CONTRACT).group(0)
        self.assertIn("trailing zeros", rule)
        self.assertIn("parentheses", rule)
        self.assertIn("$41.25M", rule)
        self.assertIn("unverified", rule)

    def test_normalisation_still_avoids_decimal_outside_the_engine_boundary(self):
        self.assertIn("no Decimal is introduced outside `engine_boundary.py`", CONTRACT)

    def test_red_test_one_covers_the_formats(self):
        one = re.search(r"\n1\. Contract:.*", TESTS).group(0)
        for case in ("$41,250,000.00", "5.50%", "($12,500)", "$41.25M"):
            self.assertIn(case, one)


class LocatorConflictTests(unittest.TestCase):
    def test_locator_keeps_candidates_that_differ_from_the_target(self):
        self.assertIn("differs from the target", LOCATOR)
        self.assertRegex(LOCATOR, r"`conflict`")

    def test_locator_does_not_filter_candidates_by_target_value_alone(self):
        self.assertNotIn("a line holding both a label and the value", LOCATOR)

    def test_conflict_is_the_one_case_a_citation_may_disagree_with_the_value(self):
        rule = re.search(r"- Two citations that disagree.*", CONTRACT).group(0)
        self.assertIn("only case", rule)

    def test_red_test_three_covers_conflict_from_the_locator(self):
        three = re.search(r"\n3\. Locator:.*", TESTS).group(0)
        self.assertRegex(three, r"same label next to two different values")


class DocumentTableTests(unittest.TestCase):
    SCHEMA = re.search(r"- Bytes live on disk.*", STORE).group(0)

    def test_blobs_and_links_are_separate_tables(self):
        self.assertIn("`blobs`", self.SCHEMA)
        self.assertIn("`deal_documents`", self.SCHEMA)
        self.assertNotIn("(sha256, deal_id, doc_name, doc_kind, size, uploaded_by, uploaded_at)", STORE)

    def test_every_column_the_lifecycle_uses_is_in_the_schema(self):
        lifecycle = STORE.split("Lifecycle contract.")[1]
        for column in ("linked_at", "uploaded_at", "orphaned_at"):
            if "`%s`" % column in lifecycle:
                self.assertIn(column, self.SCHEMA, column)

    def test_one_file_can_be_linked_to_two_deals(self):
        self.assertIn("primary key `(deal_id, sha256)`", self.SCHEMA)
        self.assertRegex(TESTS, r"linked to two deals")


class SavePathTests(unittest.TestCase):
    def test_contract_says_how_evidence_survives_and_changes_on_save(self):
        rule = re.search(r"- Saving keeps evidence honest.*", CONTRACT).group(0)
        for word in ("spec_to_view", "view_to_spec", "assumptions_engine_inputs_evidence", "manual_entry"):
            self.assertIn(word, rule)

    def test_red_test_four_covers_the_sibling_map_and_edits(self):
        four = re.search(r"\n4\. Spec round-trip:.*", TESTS).group(0)
        self.assertIn("assumptions_engine_inputs_evidence", four)
        self.assertIn("manual_entry", four)

    def test_slice_five_covers_edits_on_save(self):
        five = [x for x in SLICES.split("\n") if x.startswith("| 5 |")][0]
        self.assertIn("manual_entry", five)


class PageRotationTests(unittest.TestCase):
    def test_citation_records_rotation(self):
        self.assertIn('"rotation"', CONTRACT)

    def test_highlight_scaling_uses_height_for_y(self):
        self.assertIn("`page_height_pt` for y", FRONT)

    def test_rotated_page_is_a_fixture_and_a_red_test(self):
        self.assertRegex(TESTS, r"rotated 90 degrees")
        three = re.search(r"\n3\. Locator:.*", TESTS).group(0)
        self.assertIn("rotated", three)


if __name__ == "__main__":
    unittest.main()
