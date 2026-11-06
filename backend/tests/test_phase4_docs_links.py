"""Committed phase documents must not link to files that exist only on one machine.

A markdown link to C:/Users/... cannot be opened by anyone else and does not resolve on GitHub.
Name such a file in plain text instead.
"""
import re
from pathlib import Path

DOCS = Path(__file__).resolve().parents[2] / 'docs'
PHASE_DOCS = sorted([*DOCS.glob('PHASE-4-*.md'), *DOCS.glob('phase-3/*.md'), *DOCS.glob('phase-4/*.md')])
MACHINE_LINK = re.compile(r'\]\(\s*(?:[A-Za-z]:[/\\]|file:|/Users/|/home/)')


def test_the_phase_documents_exist():
    assert any(path.name == 'PHASE-4-MOVE-CHECKPOINT.md' for path in PHASE_DOCS)
    assert any(path.name == 'PHASE-4-OWNERSHIP-RECHECK.md' for path in PHASE_DOCS)


def test_no_phase_document_links_to_a_machine_only_path():
    offenders = [f'{path.name}:{number}' for path in PHASE_DOCS
                 for number, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1)
                 if MACHINE_LINK.search(line)]
    assert offenders == []


def test_the_named_artifacts_are_still_named():
    checkpoint = (DOCS / 'PHASE-4-MOVE-CHECKPOINT.md').read_text(encoding='utf-8')
    recheck = (DOCS / 'PHASE-4-OWNERSHIP-RECHECK.md').read_text(encoding='utf-8')
    assert 'app-remediation-001-junit.xml' in checkpoint and 'DREAM-SIX-PAGE-MEMO-BRIEF-2026-10-20.md' in checkpoint
    assert 'DREAM-PHASE4-RECEIPT-BINDING-034-001.xml' in recheck and 'DREAM-PHASE4-NATIVE-API-20261021-002' in recheck
