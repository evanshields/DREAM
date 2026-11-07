"""Committed phase documents must not link to files that exist only on one machine.

A markdown link to C:/Users/... cannot be opened by anyone else and does not resolve on GitHub.
Name such a file in plain text instead.
"""
import re
import html
from pathlib import Path
from urllib.parse import unquote

DOCS = Path(__file__).resolve().parents[2] / 'docs'
PHASE_DOCS = sorted([*DOCS.glob('PHASE-[34]-*.md'), *DOCS.glob('phase-3/**/*.md'), *DOCS.glob('phase-4/**/*.md')])
LINK_TARGET = re.compile(
    r'\]\(\s*(<[^>]+>|[^)]+)\)|^\s{0,3}\[[^\]]+\]:\s*(<[^>]+>|\S+)'
    r'|(?:href|src)\s*=\s*[\"\x27]([^\"\x27]+)[\"\x27]|<(file:[^>]+)>', re.M | re.I)


def machine_link(line, document):
    root = DOCS.parent.resolve()
    for match in LINK_TARGET.finditer(line):
        target = html.unescape(unquote(next(g for g in match.groups() if g is not None))).strip().strip('<>')
        if re.match(r'^(?:[A-Za-z]:[/\\]|file:|\\\\|/(?:Users|home|tmp|opt|root)/)', target, re.I):
            return True
        if re.match(r'^[a-z][a-z0-9+.-]*:', target, re.I) or target.startswith(('#', '/')):
            continue
        relative = target.split('#', 1)[0]
        if not (document.parent / relative).resolve().is_relative_to(root):
            return True
    return False


def test_the_phase_documents_exist():
    assert any(path.name == 'PHASE-4-MOVE-CHECKPOINT.md' for path in PHASE_DOCS)
    assert any(path.name == 'PHASE-4-OWNERSHIP-RECHECK.md' for path in PHASE_DOCS)


def test_no_phase_document_links_to_a_machine_only_path():
    offenders = [f'{path.name}:{number}' for path in PHASE_DOCS
                 for number, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1)
                 if machine_link(line, path)]
    assert offenders == []


def test_the_named_artifacts_are_still_named():
    checkpoint = (DOCS / 'PHASE-4-MOVE-CHECKPOINT.md').read_text(encoding='utf-8')
    recheck = (DOCS / 'PHASE-4-OWNERSHIP-RECHECK.md').read_text(encoding='utf-8')
    assert 'app-remediation-001-junit.xml' in checkpoint and 'DREAM-SIX-PAGE-MEMO-BRIEF-2026-10-20.md' in checkpoint
    assert 'DREAM-PHASE4-RECEIPT-BINDING-034-001.xml' in recheck and 'DREAM-PHASE4-NATIVE-API-20261021-002' in recheck
