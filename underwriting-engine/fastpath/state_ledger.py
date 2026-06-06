"""
Dream Fast-Path — durable phase-state ledger (BL-17).

The Envy run wasted real work to ephemeral context: Evan had to interrupt mid-stream to re-supply
the $75M price (the skill couldn't pull it from an image-only Transaction History PDF), Evan and
Fahd silently diverged on hold (7 vs 10) and exit cap (6.5 vs 6.25) because nothing forced a shared
assumption, and a container restart meant re-parsing the full T-12 from scratch (45 context snips of
pure waste).

This module persists a small `underwrite-state.json` SIBLING to `underwrite-spec.json` in the deal
folder (shieldstone_acquisitions/underwrites/<slug>/). It holds two things:

  1. critical_inputs  — purchase price, hold period, exit cap. Phase 0 demands these as BLOCKING
     inputs before any spread begins; once captured they survive restarts so they are never
     re-asked and never silently diverge.
  2. phase_ledger + parsed_sources — which phases completed (with a one-line result) and which
     source docs were parsed (path + a cheap fingerprint + the extracted summary), so a restart
     RESUMES from the ledger instead of re-parsing.

It does NOT replace the spec (the durable analysis->populate->memo contract) or the Claude Log
sheet (the in-workbook audit trail). It is the orchestrator's resume file: cheap, human-readable,
outside the ephemeral chat context. Pure stdlib; no openpyxl, no engine import.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional

STATE_FILENAME = "underwrite-state.json"

# The three inputs Phase 0 must capture before any spread begins (BL-17).
REQUIRED_CRITICAL_INPUTS = ("purchase_price", "hold_years", "exit_cap")


@dataclass
class CriticalInputs:
    purchase_price: Optional[float] = None
    hold_years: Optional[int] = None
    exit_cap: Optional[float] = None

    def missing(self) -> List[str]:
        return [k for k in REQUIRED_CRITICAL_INPUTS if getattr(self, k) in (None, "")]

    @property
    def complete(self) -> bool:
        return not self.missing()


@dataclass
class PhaseRecord:
    phase: int
    name: str
    status: str            # "complete" | "partial" | "blocked"
    summary: str = ""      # one-line result (carried forward in prose, not a raw dump)


@dataclass
class ParsedSource:
    path: str
    kind: str              # "t12" | "rent_roll" | "om" | "costar" | ...
    fingerprint: str       # cheap change-detector (size:mtime, or a caller-supplied hash)
    summary: str = ""      # the extracted result so a restart need not re-parse


@dataclass
class UnderwriteState:
    slug: str
    deal_name: str = ""
    routing: str = ""                                  # "ACQ" | "EFB" (Phase 0 decision)
    critical_inputs: CriticalInputs = field(default_factory=CriticalInputs)
    phase_ledger: List[PhaseRecord] = field(default_factory=list)
    parsed_sources: List[ParsedSource] = field(default_factory=list)
    updated: str = ""                                  # ISO ts, stamped by the caller (no clock here)

    # ---- critical-input gate (BL-17, the Phase-0 blocking check) ----
    def critical_inputs_ok(self) -> bool:
        return self.critical_inputs.complete

    def block_reason(self) -> str:
        miss = self.critical_inputs.missing()
        return "" if not miss else (
            "Phase 0 BLOCKED: missing required inputs before any spread — "
            + ", ".join(miss) + ". Capture purchase price, hold period, and exit cap first "
            "(BL-17: prevents the mid-stream price interruption + silent hold/exit-cap divergence).")

    # ---- phase ledger ----
    def record_phase(self, phase: int, name: str, status: str, summary: str = "") -> None:
        """Append a phase record (never overwrite a prior one — like the Claude Log)."""
        self.phase_ledger.append(PhaseRecord(phase=phase, name=name, status=status, summary=summary))

    def completed_phases(self) -> List[int]:
        return sorted({p.phase for p in self.phase_ledger if p.status == "complete"})

    def next_phase(self) -> int:
        """The lowest phase 0..12 not yet marked complete — where a restart resumes."""
        done = set(self.completed_phases())
        for p in range(0, 13):
            if p not in done:
                return p
        return 12

    # ---- parsed-source cache (resume instead of re-parse) ----
    def record_source(self, path: str, kind: str, fingerprint: str, summary: str = "") -> None:
        # replace any prior record for the same path (re-parse on a changed fingerprint)
        self.parsed_sources = [s for s in self.parsed_sources if s.path != path]
        self.parsed_sources.append(ParsedSource(path=path, kind=kind, fingerprint=fingerprint, summary=summary))

    def source_is_fresh(self, path: str, fingerprint: str) -> bool:
        """True if `path` was already parsed AND its fingerprint is unchanged (skip the re-parse)."""
        for s in self.parsed_sources:
            if s.path == path:
                return s.fingerprint == fingerprint
        return False

    def get_source_summary(self, path: str) -> Optional[str]:
        for s in self.parsed_sources:
            if s.path == path:
                return s.summary
        return None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def fingerprint_file(path: str) -> str:
    """Cheap change-detector: 'size:mtime_ns'. Avoids hashing large T-12 workbooks every check.
    A caller that wants content-stable fingerprints can pass its own hash to record_source."""
    try:
        st = os.stat(path)
        return f"{st.st_size}:{st.st_mtime_ns}"
    except OSError:
        return "missing"


def _state_path(deal_dir: str) -> str:
    return os.path.join(deal_dir, STATE_FILENAME)


def load_state(deal_dir: str, slug: Optional[str] = None) -> UnderwriteState:
    """Load the deal's state ledger, or return a fresh one if none exists (first run)."""
    p = _state_path(deal_dir)
    if not os.path.exists(p):
        return UnderwriteState(slug=slug or os.path.basename(os.path.normpath(deal_dir)))
    with open(p, "r", encoding="utf-8") as f:
        raw = json.load(f)
    ci = CriticalInputs(**raw.get("critical_inputs", {}))
    ledger = [PhaseRecord(**r) for r in raw.get("phase_ledger", [])]
    sources = [ParsedSource(**s) for s in raw.get("parsed_sources", [])]
    return UnderwriteState(
        slug=raw.get("slug", slug or ""),
        deal_name=raw.get("deal_name", ""),
        routing=raw.get("routing", ""),
        critical_inputs=ci,
        phase_ledger=ledger,
        parsed_sources=sources,
        updated=raw.get("updated", ""),
    )


def save_state(deal_dir: str, state: UnderwriteState, updated: Optional[str] = None) -> str:
    """Write the state ledger to underwrite-state.json in the deal folder. Returns the path.
    `updated` is a caller-supplied ISO timestamp (this module keeps no clock, mirroring the spec)."""
    if updated is not None:
        state.updated = updated
    os.makedirs(deal_dir, exist_ok=True)
    p = _state_path(deal_dir)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(asdict(state), f, indent=2, ensure_ascii=False)
    return p
