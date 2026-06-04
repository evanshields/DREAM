# 00: Mission Driven AI REST API + CLI Reference

## Purpose

Canonical reference for the Mission Driven AI rent + OpEx REST API. Pulled into Phase 4 (rent data), Phase 8 (agency OpEx triangulation), and Phase 12 (memo data freshness). Single source of truth for endpoint signatures, auth, and usage patterns — other references cross-link here instead of duplicating.

**Why this exists:** Anthropic's Claude.ai desktop on Windows can't complete the MCP OAuth handshake (bug `ofld_63e310c0724bb7ca` — the `claude://` callback URL scheme fails). The REST API bypasses the OAuth issue entirely. Until Anthropic ships the fix, this is the primary data path across all Claude surfaces.

---

## Base URL + auth

| Item | Value |
|---|---|
| Base URL | `https://rent-mcp.shieldstone.co/api/v1` |
| Auth header | `Authorization: Bearer $MCP_AUTH_TOKEN` |
| Token location | `c:/Users/evana/mission-driven-hud-lihtc-mcp/.secrets-vps.local` (key: `MCP_AUTH_TOKEN`) |
| Auth failure | 401 returned; check token isn't truncated (43 chars typical) |

**Token retrieval (Bash):**

```bash
TOKEN=$(grep MCP_AUTH_TOKEN c:/Users/evana/mission-driven-hud-lihtc-mcp/.secrets-vps.local | cut -d= -f2- | tr -d '"\r')
```

**Token retrieval (PowerShell):**

```powershell
$TOKEN = (Get-Content c:/Users/evana/mission-driven-hud-lihtc-mcp/.secrets-vps.local | Select-String 'MCP_AUTH_TOKEN').Line -replace 'MCP_AUTH_TOKEN=',''
```

---

## Endpoints

### Rent data (Phase 4)

| Endpoint | Query params | Returns |
|---|---|---|
| `GET /fmr` | `state, county, year, bedroom` | County-level HUD Fair Market Rent + citation |
| `GET /safmr` | `zip, year, bedroom` | ZIP-level Small Area FMR (falls back to county FMR if ZIP not in SAFMR metro) |
| `GET /lihtc` | `state, county, year, ami, bedroom` | LIHTC rent cap at one AMI tier (50, 60, etc.) |
| `GET /lihtc-table` | `state, county, year` | Full AMI × BR matrix (10 rows: 2 AMI × 5 BR) |
| `GET /counties` | `state, year` | All counties with FMR data |
| `GET /zips` | `state, county, year` | ZIPs with SAFMR data in county |
| `GET /freshness` | (none) | Ingest timestamps + row counts + source SHA256 per dataset |

### Agency OpEx benchmarks (Phase 8)

| Endpoint | Query params | Returns |
|---|---|---|
| `GET /opex/line-items` | (none) | Catalog of 13 OpEx categories |
| `GET /opex/benchmarks` | `line_item, class, state, vintage, program` | All source rows (Fannie / Freddie / HUD / Shieldstone) for a line item |
| `GET /opex/triangulate` | `line_item, class, state, vintage, program` | Binding floor + UW recommendation + all underlying sources |

**OpEx triangulation caveat:** when `program` is omitted, `binding_floor` returns MAX across ALL programs (Fannie Seniors-with-Skilled-Nursing $450/u can win for replacement reserves, etc.). For standard ACQ deals, **always pass `program=conventional`**. Verify the returned `binding_floor.citation` matches the deal context before quoting in the IC memo.

---

## Usage patterns by environment

### Claude Code (Bash + curl)

```bash
TOKEN=$(grep MCP_AUTH_TOKEN c:/Users/evana/mission-driven-hud-lihtc-mcp/.secrets-vps.local | cut -d= -f2- | tr -d '"\r')

# Rent: Denton TX 2BR FMR
curl -sS -H "Authorization: Bearer $TOKEN" \
  "https://rent-mcp.shieldstone.co/api/v1/fmr?state=TX&county=Denton&bedroom=2BR&year=2026"
# → {"fmr_dollars":1931.0, ...}

# LIHTC: full table for property
curl -sS -H "Authorization: Bearer $TOKEN" \
  "https://rent-mcp.shieldstone.co/api/v1/lihtc-table?state=FL&county=Orange&year=2026"

# OpEx: insurance binding floor for FL Class B coastal
curl -sS -H "Authorization: Bearer $TOKEN" \
  "https://rent-mcp.shieldstone.co/api/v1/opex/triangulate?line_item=insurance&class=B&state=FL_coastal&program=conventional"
```

### Claude Code or PowerShell (CLI helper, stdlib Python)

```powershell
python c:/Users/evana/mission-driven-hud-lihtc-mcp/cli/rent.py fmr TX Denton --bedroom 2BR --value
# → 1931.0

python c:/Users/evana/mission-driven-hud-lihtc-mcp/cli/rent.py lihtc TX Denton --ami 60 --bedroom 2BR --value
# → 1635.0

python c:/Users/evana/mission-driven-hud-lihtc-mcp/cli/rent.py safmr 76201 --bedroom 2BR --value
# → 1640.0

python c:/Users/evana/mission-driven-hud-lihtc-mcp/cli/rent.py opex insurance --class B --state FL_coastal

python c:/Users/evana/mission-driven-hud-lihtc-mcp/cli/rent.py opex-triangulate replacement_reserves --vintage "20+yr" --program conventional
```

Full CLI docs: `c:/Users/evana/mission-driven-hud-lihtc-mcp/docs/CLI-USAGE.md`

### Claude.ai (analysis tool, stdlib urllib)

```python
import os, json, urllib.request

token = os.environ.get('MCP_AUTH_TOKEN')  # set per-session, or read from .secrets-vps.local
def api(path, **params):
    qs = '&'.join(f'{k}={v}' for k, v in params.items())
    req = urllib.request.Request(
        f"https://rent-mcp.shieldstone.co{path}?{qs}",
        headers={'Authorization': f'Bearer {token}'})
    return json.loads(urllib.request.urlopen(req).read())

# Rent example
fmr = api('/api/v1/fmr', state='TX', county='Denton', bedroom='2BR', year=2026)

# OpEx example (note: 'class' is a Python keyword; use **{'class': 'B'})
insurance = api('/api/v1/opex/triangulate',
                line_item='insurance', state='FL_coastal',
                program='conventional', **{'class': 'B'})
```

### Claude for Excel (Power Query M)

```m
let
    Token = "PASTE_TOKEN_HERE",
    Source = Json.Document(Web.Contents(
        "https://rent-mcp.shieldstone.co/api/v1/lihtc-table?state=FL&county=Orange&year=2026",
        [Headers=[Authorization="Bearer " & Token]]))
in
    Source
```

---

## Regression baselines (verify when adopting)

| Call | Expected response |
|---|---|
| `GET /fmr?state=TX&county=Denton&bedroom=2BR&year=2026` | `fmr_dollars = 1931.0` |
| `GET /safmr?zip=76201&bedroom=2BR&year=2026` | `safmr_dollars = 1640.0` |
| `GET /lihtc?state=TX&county=Denton&ami=60&bedroom=2BR&year=2026` | `lihtc_rent_dollars = 1635.0` |
| `GET /opex/triangulate?line_item=insurance&class=B&state=FL_coastal&program=conventional` | `binding_floor.value = 900.0`, `agency = shieldstone` |

If any call drifts from these baselines without an explicit data refresh in `/freshness`, something is wrong (token expired, ingest broken, schema change). Investigate before quoting in a deal.

---

## Data freshness contract

The agency OpEx data is seeded from [references/15-opex-agency-triangulation.md](.skills/dream-underwrite/references/15-opex-agency-triangulation.md). The markdown stays canonical; the API is a read-path. When the markdown is updated (new agency manual extracted, vintage tier changed), the API needs re-seeding. Cycle:

1. Update `references/15-opex-agency-triangulation.md` per the leanness discipline
2. Re-export from markdown → seed/opex_benchmarks.json
3. Re-seed Postgres on the VPS
4. Bump the data version in `/api/v1/freshness`

Verify alignment after any seed: pull a known line item via API and compare to the markdown row.

For HUD FMR / SAFMR / LIHTC, the source of truth is HUD's published Excel files (annual). The MCP server ingests them directly; markdown extraction is not in the loop.

---

## When to read this file

- Phase 4 unit mix and rent build → pull FMR / SAFMR / LIHTC
- Phase 8 agency OpEx triangulation → pull `/opex/triangulate` per line item
- Phase 12 memo build → pull live values for memo data footnotes
- Anytime you need to validate that the rent or OpEx data the skill is operating on matches what HUD / agency manuals actually publish

## See also

- [references/03-efb-revenue.md](.skills/dream-underwrite/references/03-efb-revenue.md), EFB three-tier AMI structure consuming `/lihtc-table`
- [references/04-acq-revenue.md](.skills/dream-underwrite/references/04-acq-revenue.md), ACQ four-tier mix consuming `/fmr` + `/safmr` + `/lihtc`
- [references/15-opex-agency-triangulation.md](.skills/dream-underwrite/references/15-opex-agency-triangulation.md), Phase 8 markdown source of truth for OpEx
- [references/14-html-memo.md](.skills/dream-underwrite/references/14-html-memo.md), Phase 12 memo build pulling live citations
- Memory: `reference_mission-driven-hud-lihtc-mcp.md` (private)
- Repo: `c:/Users/evana/mission-driven-hud-lihtc-mcp/`
