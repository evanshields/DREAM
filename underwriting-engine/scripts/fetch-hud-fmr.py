"""
fetch-hud-fmr.py
================

Fetch HUD Fair Market Rents (FMR) and Small Area FMRs (SAFMR) from the
official HUD USER API and write a normalized CSV for use in the
``dream-underwrite`` underwriting workflow (Phase 4 data sourcing,
Tier 1 of the two-tier data infrastructure).

Authoritative endpoints (per https://www.huduser.gov/portal/dataset/fmr-api.html):

* ``GET /hudapi/public/fmr/listStates``
* ``GET /hudapi/public/fmr/listCounties/{state_code}``
* ``GET /hudapi/public/fmr/data/{entityid}?year=YYYY``
  where ``entityid`` is the 10-digit FIPS-based county code returned by
  ``listCounties`` (e.g. Denton County, TX = ``4812199999``).

The ``/data/{entityid}`` response shape used here::

    {
      "data": {
        "year": 2026,
        "county_name": "Denton County",
        "state_name": "Texas",
        "metro_status": "1",
        "smallarea_status": "1",
        "basicdata": [                  # ARRAY when SAFMR available
          {
            "zip_code": "MSA level",
            "Efficiency": 1234,
            "One-Bedroom": 1356,
            "Two-Bedroom": 1612,
            "Three-Bedroom": 2078,
            "Four-Bedroom": 2547
          },
          { "zip_code": "76201", "Efficiency": ..., ... },
          ...
        ]
      }
    }

For non-SAFMR areas ``basicdata`` is a single object (not an array).

Usage
-----

    # county-level only
    python fetch-hud-fmr.py --county "Denton" --state TX --year 2026

    # county-level + SAFMR for ZIP 76201
    python fetch-hud-fmr.py --county "Denton" --state TX --year 2026 --zip 76201

    # force re-fetch ignoring cache
    python fetch-hud-fmr.py --county "Denton" --state TX --year 2026 --refresh

Environment
-----------

``HUD_TOKEN`` -- Bearer token from
https://www.huduser.gov/portal/dataset/fmr-api.html
(Free signup; create token under your HUD USER account.)

PowerShell::

    $env:HUD_TOKEN = "your_long_jwt_here"

bash::

    export HUD_TOKEN="your_long_jwt_here"

Output
------

CSV at ``shieldstone_acquisitions/reference-data/<county-hyphen>-<state-lower>-<year>.csv``
unless overridden with ``--output``. Columns:

* ``bedroom_type`` - one of ``Efficiency``, ``0BR``, ``1BR``, ``2BR``, ``3BR``, ``4BR``
* ``fmr`` - county-level Fair Market Rent (USD/month, integer)
* ``safmr_<zip>`` - Small Area FMR for the supplied ZIP (only if ``--zip`` passed)

The CSV is UTF-8 with BOM for clean Excel display.
"""

from __future__ import annotations

import argparse
import csv
import datetime as _dt
import io
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

import requests


HUD_API_BASE = "https://www.huduser.gov/hudapi/public/fmr"
HUD_SIGNUP_URL = "https://www.huduser.gov/portal/dataset/fmr-api.html"
REQUEST_TIMEOUT_SEC = 30
RETRY_DELAY_SEC = 3


# ---------------------------------------------------------------------------
# HUD API client
# ---------------------------------------------------------------------------


class HudApiError(RuntimeError):
    """Raised when the HUD API returns an unrecoverable error."""


class HudClient:
    """Thin client around the HUD USER FMR API.

    One retry on transient network failure; surfaces auth errors verbatim.
    """

    def __init__(self, token: str) -> None:
        self._session = requests.Session()
        self._session.headers.update(
            {
                "Authorization": f"Bearer {token}",
                "Accept": "application/json",
                "User-Agent": "dream-underwrite/1.0 (HUD FMR fetcher)",
            }
        )

    def _get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        url = f"{HUD_API_BASE}/{path.lstrip('/')}"
        last_exc: Exception | None = None
        for attempt in (1, 2):
            try:
                resp = self._session.get(url, params=params, timeout=REQUEST_TIMEOUT_SEC)
            except requests.RequestException as exc:
                last_exc = exc
                if attempt == 1:
                    time.sleep(RETRY_DELAY_SEC)
                    continue
                raise HudApiError(
                    f"Network failure calling HUD API after retry: {exc}"
                ) from exc

            if resp.status_code in (401, 403):
                raise HudApiError(
                    "HUD API authentication failed (HTTP "
                    f"{resp.status_code}). Your HUD_TOKEN is invalid, expired, "
                    f"or unauthorized. Regenerate at {HUD_SIGNUP_URL}."
                )
            if resp.status_code == 429:
                # Rate limited (HUD documents ~60 req/min). Back off once.
                if attempt == 1:
                    time.sleep(RETRY_DELAY_SEC * 4)
                    continue
                raise HudApiError(
                    "HUD API rate limit exceeded (HTTP 429). Try again shortly."
                )
            if resp.status_code >= 500:
                if attempt == 1:
                    time.sleep(RETRY_DELAY_SEC)
                    continue
                raise HudApiError(
                    f"HUD API server error (HTTP {resp.status_code}) at {url}"
                )
            if resp.status_code >= 400:
                raise HudApiError(
                    f"HUD API client error (HTTP {resp.status_code}) at {url}: "
                    f"{resp.text[:300]}"
                )

            try:
                return resp.json()
            except json.JSONDecodeError as exc:
                raise HudApiError(
                    f"HUD API returned non-JSON response at {url}: "
                    f"{resp.text[:200]}"
                ) from exc

        # Should be unreachable; guards against fall-through.
        raise HudApiError(
            f"HUD API request failed: {last_exc!r}"
        )  # pragma: no cover

    def list_counties(self, state_code: str) -> list[dict[str, Any]]:
        """Return the county list for a state (2-letter code).

        The /listCounties/{STATE} endpoint historically returns a bare JSON
        array, but some HUD revisions wrap it in {"data": [...]}. Handle both.
        """
        payload = self._get(f"listCounties/{state_code.upper()}")
        if isinstance(payload, list):
            data = payload
        elif isinstance(payload, dict):
            data = payload.get("data", payload)
        else:
            raise HudApiError(
                f"Unexpected listCounties payload type for {state_code}: "
                f"{type(payload).__name__}"
            )
        if not isinstance(data, list):
            raise HudApiError(
                f"Unexpected listCounties response shape for {state_code}: "
                f"{type(data).__name__}"
            )
        return data

    def fmr_data(self, entity_id: str, year: int) -> dict[str, Any]:
        """Return the FMR data envelope for a county entity at a given year."""
        payload = self._get(f"data/{entity_id}", params={"year": year})
        data = payload.get("data")
        if not isinstance(data, dict):
            raise HudApiError(
                f"Unexpected fmr/data response shape for entity {entity_id}: "
                f"top-level 'data' is {type(data).__name__}"
            )
        return data


# ---------------------------------------------------------------------------
# Lookup + parse
# ---------------------------------------------------------------------------


def resolve_county_entity_id(
    counties: list[dict[str, Any]], county_name: str, state_code: str
) -> str:
    """Resolve the HUD entity id for the requested county name.

    HUD ``listCounties`` returns objects shaped like::

        {"state_code": "TX", "fips_code": "4812199999", "county_name": "Denton County", ...}

    Match is case-insensitive and tolerant of an optional trailing
    "County" / "Parish" / "Borough" / "Census Area" suffix.
    """
    needle = _normalize_county(county_name)
    for row in counties:
        raw_name = row.get("county_name") or row.get("countyname") or ""
        if _normalize_county(raw_name) == needle:
            entity = row.get("fips_code") or row.get("entityid") or row.get("entity_id")
            if not entity:
                raise HudApiError(
                    f"County '{raw_name}' has no fips_code in HUD response."
                )
            return str(entity)
    available = sorted(
        {row.get("county_name", "") for row in counties if row.get("county_name")}
    )
    sample = ", ".join(available[:10])
    raise HudApiError(
        f"No HUD county match for '{county_name}' in {state_code.upper()}. "
        f"First counties returned: {sample}"
    )


def _normalize_county(name: str) -> str:
    n = name.strip().lower()
    for suffix in (" county", " parish", " borough", " census area", " municipality"):
        if n.endswith(suffix):
            n = n[: -len(suffix)]
            break
    return n


# HUD field name -> short CSV label.
BEDROOM_FIELDS: list[tuple[str, str]] = [
    ("Efficiency", "Efficiency"),
    ("One-Bedroom", "1BR"),
    ("Two-Bedroom", "2BR"),
    ("Three-Bedroom", "3BR"),
    ("Four-Bedroom", "4BR"),
]


def extract_county_rents(envelope: dict[str, Any]) -> dict[str, int | None]:
    """Pull the county-level (or MSA-level) FMR row from the envelope.

    ``basicdata`` is either:
      * a single dict (non-SAFMR area)
      * a list whose first element has ``zip_code == "MSA level"`` followed by
        per-ZIP rows (SAFMR area)
    """
    basic = envelope.get("basicdata")
    if isinstance(basic, dict):
        return _row_to_rents(basic)
    if isinstance(basic, list) and basic:
        # First record is the MSA/county-level summary in SAFMR responses.
        msa_row = next(
            (r for r in basic if str(r.get("zip_code", "")).lower() == "msa level"),
            basic[0],
        )
        return _row_to_rents(msa_row)
    raise HudApiError("HUD response had no 'basicdata' rents.")


def extract_safmr_rents(
    envelope: dict[str, Any], zip_code: str
) -> dict[str, int | None] | None:
    """Pull the ZIP-level SAFMR row if present; else return ``None``."""
    if str(envelope.get("smallarea_status", "")) != "1":
        return None
    basic = envelope.get("basicdata")
    if not isinstance(basic, list):
        return None
    needle = zip_code.strip().zfill(5)
    for row in basic:
        if str(row.get("zip_code", "")).strip() == needle:
            return _row_to_rents(row)
    return None


def _row_to_rents(row: dict[str, Any]) -> dict[str, int | None]:
    out: dict[str, int | None] = {}
    for hud_key, _short_label in BEDROOM_FIELDS:
        value = row.get(hud_key)
        out[hud_key] = _coerce_int(value)
    return out


def _coerce_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(round(float(value)))
    except (TypeError, ValueError):
        return None


# ---------------------------------------------------------------------------
# CSV emit
# ---------------------------------------------------------------------------


def write_csv(
    output_path: Path,
    county_rents: dict[str, int | None],
    safmr_rents: dict[str, int | None] | None,
    safmr_zip: str | None,
    metadata: dict[str, Any],
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    safmr_col = f"safmr_{safmr_zip}" if safmr_zip else None
    has_efficiency = (
        county_rents.get("Efficiency") is not None
        or (safmr_rents or {}).get("Efficiency") is not None
    )

    headers: list[str] = ["bedroom_type", "fmr"]
    if safmr_col:
        headers.append(safmr_col)

    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\n")

    # Metadata header rows as CSV comments. Excel tolerates leading '#'.
    writer.writerow([f"# HUD FMR fetch -- generated {metadata['fetched_at']}"])
    writer.writerow([f"# county={metadata['county']}, state={metadata['state']}, year={metadata['year']}"])
    writer.writerow([f"# entity_id={metadata['entity_id']}, smallarea_status={metadata['smallarea_status']}"])
    if safmr_col and safmr_rents is None:
        writer.writerow(
            [f"# WARNING: ZIP {safmr_zip} returned no SAFMR row -- column left blank"]
        )
    writer.writerow([])  # blank row separates metadata from data
    writer.writerow(headers)

    for hud_key, short_label in BEDROOM_FIELDS:
        if hud_key == "Efficiency" and not has_efficiency:
            continue
        row: list[str] = [short_label, _fmt(county_rents.get(hud_key))]
        if safmr_col:
            row.append(_fmt((safmr_rents or {}).get(hud_key)))
        writer.writerow(row)

    # UTF-8 BOM so Excel auto-detects encoding.
    output_path.write_text(buf.getvalue(), encoding="utf-8-sig", newline="")


def _fmt(value: int | None) -> str:
    return "" if value is None else str(value)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _repo_root() -> Path:
    """Return the shieldstone_os repo root.

    The script lives at ``<repo>/.skills/dream-underwrite/scripts/`` --
    walk up four levels. Falls back to cwd if that path doesn't look right.
    """
    here = Path(__file__).resolve()
    candidate = here.parents[3] if len(here.parents) >= 4 else Path.cwd()
    return candidate


def _default_output(county: str, state: str, year: int) -> Path:
    slug_county = county.strip().lower().replace(" ", "-")
    slug_state = state.strip().lower()
    return (
        _repo_root()
        / "shieldstone_acquisitions"
        / "reference-data"
        / f"{slug_county}-{slug_state}-{year}.csv"
    )


def _current_fy() -> int:
    # HUD fiscal year is the same calendar year for FMR effective Oct 1 prior.
    # Default to current calendar year; user can override with --year.
    return _dt.date.today().year


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="fetch-hud-fmr.py",
        description=(
            "Fetch HUD Fair Market Rents (and optional Small Area FMR by ZIP) "
            "from the HUD USER API and write a normalized CSV for the "
            "dream-underwrite skill."
        ),
        epilog=(
            "Token required: set HUD_TOKEN env var. Register at "
            f"{HUD_SIGNUP_URL}."
        ),
    )
    parser.add_argument(
        "--county",
        required=True,
        help='County name (without "County" suffix), e.g. "Denton"',
    )
    parser.add_argument(
        "--state",
        required=True,
        help="USPS 2-letter state code, e.g. TX",
    )
    parser.add_argument(
        "--year",
        type=int,
        default=_current_fy(),
        help="HUD fiscal year (defaults to current calendar year)",
    )
    parser.add_argument(
        "--zip",
        dest="zip_code",
        default=None,
        help="Optional 5-digit ZIP to also fetch Small Area FMR for",
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Force re-fetch even if cached CSV exists",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help=(
            "Output CSV path. Defaults to "
            "shieldstone_acquisitions/reference-data/"
            "<county>-<state>-<year>.csv"
        ),
    )
    return parser.parse_args(argv)


def _get_token() -> str:
    token = os.environ.get("HUD_TOKEN", "").strip()
    if not token:
        print(
            "ERROR: HUD_TOKEN environment variable is not set.\n"
            f"Register for a free token at: {HUD_SIGNUP_URL}\n"
            "Then set it for this session:\n"
            '  PowerShell:  $env:HUD_TOKEN = "<your-token>"\n'
            '  bash:        export HUD_TOKEN="<your-token>"',
            file=sys.stderr,
        )
        raise SystemExit(2)
    return token


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)

    if len(args.state) != 2 or not args.state.isalpha():
        print(
            f"ERROR: --state must be a 2-letter code, got {args.state!r}",
            file=sys.stderr,
        )
        return 2
    state = args.state.upper()
    county = args.county.strip()

    if args.zip_code is not None:
        z = args.zip_code.strip()
        if not (z.isdigit() and len(z) == 5):
            print(
                f"ERROR: --zip must be a 5-digit ZIP code, got {args.zip_code!r}",
                file=sys.stderr,
            )
            return 2
        zip_code: str | None = z
    else:
        zip_code = None

    output_path: Path = args.output or _default_output(county, state, args.year)

    if output_path.exists() and not args.refresh:
        print(
            f"[cache] CSV already exists at {output_path}\n"
            "        Pass --refresh to force re-fetch."
        )
        return 0

    token = _get_token()
    client = HudClient(token)

    try:
        counties = client.list_counties(state)
        entity_id = resolve_county_entity_id(counties, county, state)
        envelope = client.fmr_data(entity_id, args.year)
        county_rents = extract_county_rents(envelope)
        safmr_rents = (
            extract_safmr_rents(envelope, zip_code) if zip_code else None
        )
    except HudApiError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if zip_code and safmr_rents is None:
        smallarea = str(envelope.get("smallarea_status", "0")) == "1"
        if smallarea:
            print(
                f"WARNING: ZIP {zip_code} not found in SAFMR rows for "
                f"{county}, {state}. CSV will include SAFMR column with blanks.",
                file=sys.stderr,
            )
        else:
            print(
                f"WARNING: {county}, {state} is not a Small Area FMR metro for "
                f"FY{args.year}. SAFMR column will be blank.",
                file=sys.stderr,
            )

    metadata = {
        "fetched_at": _dt.datetime.now().isoformat(timespec="seconds"),
        "county": envelope.get("county_name") or county,
        "state": envelope.get("state_name") or state,
        "year": envelope.get("year") or args.year,
        "entity_id": entity_id,
        "smallarea_status": envelope.get("smallarea_status", "0"),
    }

    write_csv(output_path, county_rents, safmr_rents, zip_code, metadata)

    print(f"OK    wrote {output_path}")
    print(
        f"      county={metadata['county']}, state={metadata['state']}, "
        f"year={metadata['year']}, entity_id={entity_id}"
    )
    if zip_code:
        if safmr_rents:
            print(f"      SAFMR rents included for ZIP {zip_code}")
        else:
            print(f"      SAFMR column for ZIP {zip_code} is blank (see warning)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
