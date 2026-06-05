# `dream-underwrite` Scripts

Tier 1 data-sourcing utilities for the `dream-underwrite` underwriting skill.

## Purpose

These scripts pull rent and benchmark data from official sources into the codebase as cached CSVs so the master underwriting skill can populate Phase 4 (Unit Mix and Rent Tiers) and Phase 11 (Comps tab) without round-tripping to the web every session. They are the local fallback layer of the two-tier data infrastructure described in Section 5 of the plan; the Tier 2 HUD/AMI MCP server on the US VPS will eventually call the same underlying APIs and obsolete the local cache for connected sessions. Until then, every deal gets one CSV per county per fiscal year sitting in [shieldstone_acquisitions/reference-data/](../../../shieldstone_acquisitions/reference-data/).

Currently shipping:

- [fetch-hud-fmr.py](fetch-hud-fmr.py) -- HUD Fair Market Rents + Small Area FMR by ZIP
- [repackage-skill.py](repackage-skill.py) -- rebuild the Claude.ai-uploadable `.zip` and `.skill` bundles into `~/Downloads/` after editing any file in this skill. Run after every change so the Downloads bundle stays in sync with the source folder. Add `--verify` to list the bundle contents.

## Installation

The script uses Python 3.9+ stdlib plus `requests`. From the repo root:

```powershell
pip install -r .skills/dream-underwrite/scripts/requirements.txt
```

Or directly:

```powershell
pip install requests==2.32.3
```

## HUD token setup

The HUD USER API requires a Bearer token. It is free; signup takes about two minutes.

1. Register at [HUD USER FMR API](https://www.huduser.gov/portal/dataset/fmr-api.html) and confirm your email.
2. Log in, open the API page, and click **Create New Token**. Copy the JWT string.
3. Set the token as an environment variable for the current shell:

   PowerShell (Windows):

   ```powershell
   $env:HUD_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9..."
   ```

   bash / zsh (macOS / Linux):

   ```bash
   export HUD_TOKEN="eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9..."
   ```

   To make it persistent on Windows, add the variable through **System Properties -> Environment Variables** instead of inline.

The script reads `HUD_TOKEN` at runtime only. The token is never written to disk by this script.

## Usage

County-level FMR only (Denton County, TX, FY 2026):

```powershell
python .skills/dream-underwrite/scripts/fetch-hud-fmr.py --county "Denton" --state TX --year 2026
```

Expected output:

```text
OK    wrote C:\Users\evana\shieldstone_os\shieldstone_acquisitions\reference-data\denton-tx-2026.csv
      county=Denton County, state=Texas, year=2026, entity_id=4812199999
```

County-level FMR plus Small Area FMR for ZIP 76201:

```powershell
python .skills/dream-underwrite/scripts/fetch-hud-fmr.py --county "Denton" --state TX --year 2026 --zip 76201
```

Force re-fetch ignoring the cached CSV:

```powershell
python .skills/dream-underwrite/scripts/fetch-hud-fmr.py --county "Denton" --state TX --year 2026 --refresh
```

Custom output path:

```powershell
python .skills/dream-underwrite/scripts/fetch-hud-fmr.py --county "Denton" --state TX --year 2026 --output "C:/tmp/denton.csv"
```

CLI help:

```powershell
python .skills/dream-underwrite/scripts/fetch-hud-fmr.py --help
```

## Output format

Default location: [shieldstone_acquisitions/reference-data/](../../../shieldstone_acquisitions/reference-data/)`<county-hyphenated>-<state-lower>-<year>.csv`

The CSV is UTF-8 with BOM so Excel opens it cleanly. The top of the file carries a few comment rows (lines beginning with `#`) recording the fetch timestamp, county, state, year, HUD entity id, and small-area status. A blank row separates the metadata from the data table.

Columns in the data table:

| Column | Type | Description |
|---|---|---|
| `bedroom_type` | string | One of `Efficiency`, `1BR`, `2BR`, `3BR`, `4BR`. The `Efficiency` row is omitted if HUD returns no efficiency rent for the area. |
| `fmr` | integer USD/month | County-level (or MSA-level) HUD FMR. Always present. |
| `safmr_<zip>` | integer USD/month | Small Area FMR for the requested ZIP. Column appears only when `--zip` is supplied. Blank if the ZIP is outside a SAFMR metro. |

Example for `denton-tx-2026.csv` with `--zip 76201`:

```csv
# HUD FMR fetch -- generated 2026-05-13T14:22:01
# county=Denton County, state=Texas, year=2026
# entity_id=4812199999, smallarea_status=1

bedroom_type,fmr,safmr_76201
1BR,1356,1410
2BR,1612,1670
3BR,2078,2150
4BR,2547,2620
```

## Novogradac note

**Novogradac LIHTC rents are NOT fetched by this script.** Anti-bot protections on `rent-income.novoco.com` block automation. Phase 4 of the [dream-underwrite](../SKILL.md) skill uses a pause-and-paste pattern instead: the skill provides the Novogradac URL with pre-filled query parameters, the user opens it in a browser, copies the LIHTC rent table for the target county, and pastes it back into the Claude for Excel chat. The skill ingests the pasted table and continues underwriting. The Tier 2 MCP server on the US VPS will load Novogradac's annual FY rent-limit Excel files in bulk (those releases are NOT anti-bot protected, only the calculator UI is), at which point the pause-and-paste pattern can retire.

## Troubleshooting

**`ERROR: HUD_TOKEN environment variable is not set.`**
The script could not find a Bearer token in the environment. Follow the HUD token setup section above. Confirm with `$env:HUD_TOKEN` (PowerShell) or `echo $HUD_TOKEN` (bash) that the variable is set in the same shell you are running the script from.

**`HUD API authentication failed (HTTP 401)` or `(HTTP 403)`**
Your token is invalid, expired, or revoked. Log back into [HUD USER](https://www.huduser.gov/portal/dataset/fmr-api.html), regenerate the token, and reset `HUD_TOKEN`.

**`No HUD county match for '<name>' in <state>.`**
HUD's county_name does not match the value you passed. Try the official name without the "County" suffix (the script strips it automatically): use `--county "Miami-Dade"`, not `--county "Miami Dade County"`. The error message lists the first 10 counties HUD returned so you can verify spelling. For independent cities (Virginia) or boroughs (Alaska), use the full local name minus the suffix.

**`HUD API rate limit exceeded (HTTP 429).`**
HUD throttles at roughly 60 requests per minute. The script retries once with backoff before surfacing this error. Wait a minute and rerun, or batch multiple counties with `sleep 2` between calls.

**`Network failure calling HUD API after retry`**
Transient connectivity issue. Rerun. If it persists, check `https://www.huduser.gov` is reachable from this network and that no corporate proxy is intercepting the request.

**`WARNING: ZIP <zip> not found in SAFMR rows for <county>.`**
The county is a SAFMR metro but the specific ZIP you requested is not in the HUD basicdata array. Double-check the ZIP is inside the county. The CSV still writes with a blank SAFMR column.

**`WARNING: <county>, <state> is not a Small Area FMR metro for FY<year>.`**
SAFMR data only exists for designated metro areas (Dallas-Fort Worth, Atlanta, Houston, etc. -- the HUD SAFMR list is at [HUD SAFMR](https://www.huduser.gov/portal/datasets/fmr/smallarea/index.html)). For non-SAFMR areas the county FMR is the only available HUD rent benchmark. Drop `--zip` or accept the blank SAFMR column.

**Output CSV opens with garbled characters in Excel.**
The file is UTF-8 with BOM. If Excel still misreads it, open Excel first, then **Data -> From Text/CSV** and select **65001: Unicode (UTF-8)** as the file origin.
