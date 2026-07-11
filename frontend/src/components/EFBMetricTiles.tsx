import { useMemo, useState } from 'react';
import { TrendingUp } from 'lucide-react';
import {
  underwriteEFB,
  type EFBUnderwriteRequest,
  type EFBHeadlineMetrics,
} from '../lib/api';
import { Card } from './ui';
import { fmtUSD, fmtUSDFull, fmtPct, fmtEM } from '../lib/format';
import { NumField, StatusLine, useLiveCalc } from './livecalc';

// ---------------------------------------------------------------------------
// Shared EFB metric presentation + live sizing panel.
//   - EFBMetricTiles: the four headline tiles (Max Bond Proceeds / Annual Debt
//     Service / Year-1 DSCR / Tax Savings) + the small stat echo strip. Pure
//     display — used for the CP-1 snapshot on DealDetail and inside the panel.
//   - EFBSizingPanel: BondScreen's live-recalc bond sizing (POST
//     /api/underwrite/efb), optionally seeded from a deal's headline metrics.
// ---------------------------------------------------------------------------

// Backend EFBUnderwriteRequest defaults; stabilized_noi has no backend default,
// so we seed a representative workforce-housing NOI as the starting point.
export const EFB_SIZING_DEFAULTS: EFBUnderwriteRequest = {
  stabilized_noi: 2_500_000,
  target_dscr: 1.15,
  bond_rate: 0.05,
  amortization_years: 35,
  annual_property_tax_exempted: null,
  hold_years: 10,
};

export function EFBMetricTiles({
  hm,
  holdYears = 10,
  loading = false,
}: {
  hm: Partial<EFBHeadlineMetrics> | null;
  holdYears?: number;
  loading?: boolean;
}) {
  const tiles = useMemo(
    () => [
      {
        label: 'Max Bond Proceeds',
        value: hm?.bond_amount != null ? fmtUSD(hm.bond_amount) : '—',
        sub: 'Largest bond the NOI supports at the target DSCR',
      },
      {
        label: 'Annual Debt Service',
        value: hm?.annual_debt_service != null ? fmtUSDFull(hm.annual_debt_service) : '—',
        sub: 'Yearly bond payment on the sized amount',
      },
      {
        label: 'Year-1 DSCR',
        value: hm?.year1_dscr != null ? fmtEM(hm.year1_dscr) : '—',
        sub: 'Stabilized NOI over annual debt service',
      },
      {
        label: `Tax Savings (${holdYears}-Yr)`,
        value: hm?.tax_savings_10yr != null ? fmtUSD(hm.tax_savings_10yr) : '—',
        sub:
          hm?.tax_savings_10yr != null
            ? 'Property tax exempted over the hold'
            : 'Enter annual property tax exempted to compute',
      },
    ],
    [hm, holdYears],
  );

  return (
    <div className="space-y-6">
      {/* headline tiles */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {tiles.map((t) => (
          <Card
            key={t.label}
            className={`p-5 flex flex-col justify-between h-full border-t-4 border-t-teal ${
              loading ? 'opacity-60' : ''
            }`}
          >
            <span className="eyebrow text-slate/50">{t.label}</span>
            <div className="font-head font-bold text-3xl lg:text-4xl text-teal tnum mt-2">
              {t.value}
            </div>
            <div className="mt-2 text-xs text-slate/50">{t.sub}</div>
          </Card>
        ))}
      </div>

      {/* secondary echo strip */}
      {hm && (
        <div className="flex flex-wrap gap-x-6 gap-y-1 text-xs text-slate/60 tnum">
          <span>
            Max supportable debt service:{' '}
            <b className="text-slate">
              {hm.maximum_debt_service != null ? fmtUSDFull(hm.maximum_debt_service) : '—'}
            </b>
          </span>
          <span>
            Stabilized NOI:{' '}
            <b className="text-slate">{hm.year1_noi != null ? fmtUSDFull(hm.year1_noi) : '—'}</b>
          </span>
          <span>
            Target DSCR:{' '}
            <b className="text-slate">{hm.target_dscr != null ? fmtEM(hm.target_dscr) : '—'}</b>
          </span>
          <span>
            Bond rate:{' '}
            <b className="text-slate">{hm.bond_rate != null ? fmtPct(hm.bond_rate) : '—'}</b>
          </span>
        </div>
      )}
    </div>
  );
}

export function EFBSizingPanel({
  seed,
  title = 'Bond Sizing',
}: {
  seed?: Partial<EFBUnderwriteRequest>;
  title?: string;
}) {
  // seed is applied once, at mount — callers render this only once the deal /
  // job headline metrics are resolved.
  const [req, setReq] = useState<EFBUnderwriteRequest>({ ...EFB_SIZING_DEFAULTS, ...seed });
  const { result, loading, error } = useLiveCalc(underwriteEFB, req);
  const hm: EFBHeadlineMetrics | null = result?.headline_metrics ?? null;

  const set = (patch: Partial<EFBUnderwriteRequest>) => setReq((prev) => ({ ...prev, ...patch }));

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="eyebrow text-slate/60 flex items-center">
          <TrendingUp className="w-4 h-4 mr-2" /> {title}
        </h2>
        <StatusLine loading={loading} error={error} />
      </div>

      <EFBMetricTiles hm={hm} holdYears={req.hold_years} loading={loading} />

      {/* inputs */}
      <Card className="p-5">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          <NumField
            label="Stabilized NOI"
            kind="usd"
            value={req.stabilized_noi}
            hint="Year-1 stabilized net operating income"
            onCommit={(v) => v != null && set({ stabilized_noi: v })}
          />
          <NumField
            label="Target DSCR"
            kind="ratio"
            value={req.target_dscr}
            hint="1.15x with HAP · 1.20x without"
            onCommit={(v) => v != null && set({ target_dscr: v })}
          />
          <NumField
            label="Bond Rate"
            kind="pct"
            value={req.bond_rate}
            hint="Tax-exempt bond coupon"
            onCommit={(v) => v != null && set({ bond_rate: v })}
          />
          <NumField
            label="Amortization (Years)"
            kind="int"
            value={req.amortization_years}
            hint="35-yr standard for bond deals"
            onCommit={(v) => v != null && set({ amortization_years: v })}
          />
          <NumField
            label="Annual Property Tax Exempted"
            kind="usd"
            value={req.annual_property_tax_exempted ?? null}
            hint="Optional · drives the tax-savings tile only, not sizing"
            optional
            onCommit={(v) => set({ annual_property_tax_exempted: v })}
          />
          <NumField
            label="Hold Years"
            kind="int"
            value={req.hold_years}
            hint="10-yr hold + ROFR standard"
            onCommit={(v) => v != null && set({ hold_years: v })}
          />
        </div>
      </Card>
    </div>
  );
}
