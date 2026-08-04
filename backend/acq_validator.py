"""
ACQ deal validator (Wave B.2) — GREEN/AMBER/RED flags for a COMPUTED conventional (ACQ) deal.

The existing `calculations/validator.py` (DealValidator) validates EFB *inputs* vs the T-Manual and
is left untouched. This module is the ACQ complement: it takes the engine's computed
`headline_metrics` + a few deal assumptions and flags them against the Shieldstone V2.0 acquisitions
standards + the BL fee-bounds gate. It reuses the validated engine gate (`assert_fee_bounds`) so the
server validator and the populate path never disagree.

Standards (from acquisitions-standards.md / memory):
  - Min levered IRR by market tier: Gateway 14% / Secondary 16% / Tertiary 18%.
  - Min equity multiple: 1.5x all markets.
  - Exit cap >= entry (going-in) cap — never embed compression (RED if violated).
  - Min DSCR: bridge years >= 1.10x, refi/stabilized years >= 1.25x.
  - Acquisition fee within ACQ bounds (0.5-1.0%); the 5% EFB sentinel is a RED.

Flags use the same {field, status, message, ...} shape as the app's ValidationFlag so the API
response is uniform.
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Dict, List, Optional

_ENGINE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "underwriting-engine", "engine",
)
if _ENGINE_DIR not in sys.path:
    sys.path.insert(0, _ENGINE_DIR)

from acq_engine import assert_fee_bounds  # noqa: E402


# Min levered IRR by market tier (Shieldstone V2.0).
TIER_MIN_IRR = {"GATEWAY": 0.14, "SECONDARY": 0.16, "TERTIARY": 0.18}
MIN_EQUITY_MULTIPLE = 1.5
BRIDGE_DSCR_FLOOR = 1.10
REFI_DSCR_FLOOR = 1.25


@dataclass
class ACQFlag:
    field: str
    status: str          # GREEN | AMBER | RED
    message: str
    benchmark: str = ""
    current_value: object = None

    def as_dict(self) -> Dict[str, object]:
        return {
            "field": self.field, "status": self.status, "message": self.message,
            "benchmark": self.benchmark, "current_value": self.current_value,
            "section": "ACQ", "manual_ref": "acquisitions-standards.md V2.0",
        }


def validate_acq(
    headline_metrics: Dict[str, object],
    *,
    market_tier: str = "SECONDARY",
    going_in_cap: Optional[float] = None,
    exit_cap: Optional[float] = None,
    acquisition_fee_pct: Optional[float] = None,
    fee_override: bool = False,
    bridge_io_years: int = 2,
) -> List[ACQFlag]:
    """Validate a computed ACQ deal. Returns GREEN/AMBER/RED flags."""
    flags: List[ACQFlag] = []
    tier = str(market_tier).upper()
    min_irr = TIER_MIN_IRR.get(tier, TIER_MIN_IRR["SECONDARY"])

    # --- IRR vs tier hurdle ---
    irr = headline_metrics.get("irr")
    if irr is not None:
        if irr >= min_irr:
            flags.append(ACQFlag("irr", "GREEN", f"IRR {irr:.1%} clears {tier} hurdle {min_irr:.0%}",
                                 benchmark=f">= {min_irr:.0%}", current_value=irr))
        elif irr >= min_irr - 0.02:
            flags.append(ACQFlag("irr", "AMBER", f"IRR {irr:.1%} within 2pts of {tier} hurdle {min_irr:.0%}",
                                 benchmark=f">= {min_irr:.0%}", current_value=irr))
        else:
            flags.append(ACQFlag("irr", "RED", f"IRR {irr:.1%} below {tier} hurdle {min_irr:.0%}",
                                 benchmark=f">= {min_irr:.0%}", current_value=irr))

    # --- equity multiple ---
    em = headline_metrics.get("equity_multiple")
    if em is not None:
        status = "GREEN" if em >= MIN_EQUITY_MULTIPLE else ("AMBER" if em >= MIN_EQUITY_MULTIPLE - 0.1 else "RED")
        flags.append(ACQFlag("equity_multiple", status,
                             f"EM {em:.2f}x vs floor {MIN_EQUITY_MULTIPLE:.1f}x",
                             benchmark=f">= {MIN_EQUITY_MULTIPLE:.1f}x", current_value=em))

    # --- exit >= entry (never embed compression) ---
    if going_in_cap is not None and exit_cap is not None:
        if exit_cap >= going_in_cap:
            flags.append(ACQFlag("exit_cap", "GREEN",
                                 f"exit cap {exit_cap:.2%} >= entry {going_in_cap:.2%}",
                                 benchmark=">= going-in cap", current_value=exit_cap))
        else:
            flags.append(ACQFlag("exit_cap", "RED",
                                 f"exit cap {exit_cap:.2%} < entry {going_in_cap:.2%} — embeds compression",
                                 benchmark=">= going-in cap", current_value=exit_cap))

    # --- DSCR floors per loan phase ---
    dscr_series = headline_metrics.get("dscr_series") or []
    for i, dscr in enumerate(dscr_series):
        year = i + 1
        floor = BRIDGE_DSCR_FLOOR if year <= bridge_io_years else REFI_DSCR_FLOOR
        if dscr is None:
            continue
        if dscr < floor:
            flags.append(ACQFlag(f"dscr_year{year}", "RED",
                                 f"Year {year} DSCR {dscr:.2f} below floor {floor:.2f}",
                                 benchmark=f">= {floor:.2f}", current_value=dscr))
    # one GREEN summary if all DSCR years pass
    if dscr_series and not any(fl.field.startswith("dscr_year") for fl in flags):
        flags.append(ACQFlag("dscr", "GREEN", "all DSCR years clear their phase floor",
                             benchmark="bridge >=1.10x / refi >=1.25x", current_value=min(dscr_series)))

    # --- acquisition fee bounds (reuse the engine gate) ---
    if acquisition_fee_pct is not None:
        res = assert_fee_bounds(Decimal(str(acquisition_fee_pct)), routing="ACQ", override=fee_override)
        flags.append(ACQFlag("acquisition_fee_pct", "GREEN" if res.ok else "RED",
                             res.reason, benchmark="0.5%-1.0% (ACQ)",
                             current_value=acquisition_fee_pct))

    return flags


def summarize(flags: List[ACQFlag]) -> Dict[str, object]:
    green = sum(1 for f in flags if f.status == "GREEN")
    amber = sum(1 for f in flags if f.status == "AMBER")
    red = sum(1 for f in flags if f.status == "RED")
    pass_fail = "FAIL" if red else ("REVIEW" if amber else "PASS")
    return {"total": len(flags), "green_count": green, "amber_count": amber,
            "red_count": red, "pass_fail": pass_fail}
