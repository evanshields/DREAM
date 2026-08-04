import { useState } from 'react';
import {
  Landmark,
  Activity,
  RotateCcw,
  Crosshair,
  Building2,
  Info,
} from 'lucide-react';
import {
  recalcExitCap,
  recalcAgencySizing,
  type ExitCapRequest,
  type ExitCapResponse,
  type ExitCapStrategy,
  type AgencySizingRequest,
  type AgencySizingResponse,
} from '../lib/api';
import { Card, Button, Badge } from '../components/ui';
import { fmtUSD, fmtPct } from '../lib/format';
import { NumField, StatusLine, useLiveCalc } from '../components/livecalc';
import { EFBSizingPanel } from '../components/EFBMetricTiles';

// ---------------------------------------------------------------------------
// Bond Screen — deterministic 501(c)(3)/EFB tax-exempt bond sizing.
// Three LLM-free endpoints (backend/routers/recalc.py):
//   POST /api/underwrite/efb      — size bonds to a target DSCR on stabilized NOI
//   POST /api/recalc/exit-cap     — 3-method exit-cap triangulation (takes HIGHEST)
//   POST /api/recalc/agency-sizing — takeout loan = MIN(DSCR, LTV, debt-yield)
// Defaults mirror the backend request models exactly. The EFB sizing panel +
// the live-recalc field primitives live in src/components (shared with the
// EFB deal-detail view).
// ---------------------------------------------------------------------------

// ===========================================================================
// Exit-cap triangulation (companion)
// ===========================================================================

const EXIT_CAP_DEFAULTS: ExitCapRequest = {
  going_in_cap: 0.055,
  strategy: 'value_add',
  forward_treasury: null,
  agency_spread: 0.015,
  neg_leverage_buffer: 0.0075,
  comp_implied_cap: null,
};

const STRATEGIES: { key: ExitCapStrategy; label: string }[] = [
  { key: 'core', label: 'Core (+35 bps)' },
  { key: 'core_plus', label: 'Core Plus (+62.5 bps)' },
  { key: 'value_add', label: 'Value-Add (+100 bps)' },
  { key: 'opportunistic', label: 'Opportunistic (+150 bps)' },
];

const BINDING_LABELS: Record<string, string> = {
  'entry+strategy': 'Entry + Strategy',
  treasury_spread: 'Treasury Spread',
  comp_validation: 'Comp Validation',
};

function ExitCapPanel() {
  const [req, setReq] = useState<ExitCapRequest>(EXIT_CAP_DEFAULTS);
  const { result, loading, error } = useLiveCalc(recalcExitCap, req);
  const r: ExitCapResponse | null = result;

  const set = (patch: Partial<ExitCapRequest>) => setReq((prev) => ({ ...prev, ...patch }));

  // method_treasury comes back 0 when no forward treasury was supplied — show as not run.
  const methods = [
    {
      label: 'Treasury Spread',
      key: 'treasury_spread',
      value: r?.method_treasury != null && r.method_treasury > 0 ? r.method_treasury : null,
    },
    { label: 'Comp Validation', key: 'comp_validation', value: r?.method_comp ?? null },
    { label: 'Entry + Strategy', key: 'entry+strategy', value: r?.method_entry_strategy ?? null },
  ];

  return (
    <Card className="p-6 flex flex-col">
      <div className="flex items-center justify-between mb-1">
        <h3 className="text-lg font-head font-semibold text-slate flex items-center">
          <Crosshair className="w-5 h-5 mr-2 text-teal" /> Exit-Cap Triangulation
        </h3>
        <StatusLine loading={loading} error={error} />
      </div>
      <p className="text-xs text-slate/50 mb-5">
        Three methods, takes the HIGHEST (most conservative) as the exit cap.
      </p>

      {/* result */}
      <div className={`mb-5 ${loading ? 'opacity-60' : ''}`}>
        <div className="flex items-end gap-3">
          <span className="font-head font-bold text-4xl text-teal tnum">
            {r?.exit_cap != null ? fmtPct(r.exit_cap) : '—'}
          </span>
          {r?.binding_method && (
            <Badge tone="teal" className="mb-1.5">
              binding: {BINDING_LABELS[r.binding_method] ?? r.binding_method}
            </Badge>
          )}
        </div>
        <div className="mt-3 divide-y divide-slate/10 text-sm">
          {methods.map((m) => {
            const isBinding = r?.binding_method === m.key && m.value != null;
            return (
              <div key={m.key} className="flex items-center justify-between py-1.5">
                <span className={isBinding ? 'font-semibold text-teal' : 'text-slate/70'}>
                  {m.label}
                </span>
                <span className={`tnum ${isBinding ? 'font-semibold text-teal' : 'text-slate'}`}>
                  {m.value != null ? fmtPct(m.value) : '—'}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {/* inputs */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-auto">
        <NumField
          label="Going-In Cap"
          kind="pct"
          value={req.going_in_cap}
          onCommit={(v) => v != null && set({ going_in_cap: v })}
        />
        <div>
          <div className="flex items-center justify-between mb-1.5">
            <label className="text-sm font-semibold text-slate">Strategy</label>
            <Badge tone="neutral">enum</Badge>
          </div>
          <select
            value={req.strategy}
            onChange={(e) => set({ strategy: e.target.value as ExitCapStrategy })}
            className="input"
            aria-label="Strategy"
          >
            {STRATEGIES.map((s) => (
              <option key={s.key} value={s.key}>
                {s.label}
              </option>
            ))}
          </select>
        </div>
        <NumField
          label="Forward Treasury"
          kind="pct"
          value={req.forward_treasury ?? null}
          hint="Optional · enables the Treasury-spread method"
          optional
          onCommit={(v) => set({ forward_treasury: v })}
        />
        <NumField
          label="Comp-Implied Cap"
          kind="pct"
          value={req.comp_implied_cap ?? null}
          hint="Optional · enables the comp-validation method"
          optional
          onCommit={(v) => set({ comp_implied_cap: v })}
        />
        <NumField
          label="Agency Spread"
          kind="pct"
          value={req.agency_spread}
          onCommit={(v) => v != null && set({ agency_spread: v })}
        />
        <NumField
          label="Neg-Leverage Buffer"
          kind="pct"
          value={req.neg_leverage_buffer}
          onCommit={(v) => v != null && set({ neg_leverage_buffer: v })}
        />
      </div>
    </Card>
  );
}

// ===========================================================================
// Agency takeout sizing (companion)
// ===========================================================================

const AGENCY_DEFAULTS: AgencySizingRequest = {
  stabilized_noi: 2_500_000,
  stabilized_value: 40_000_000,
  refi_rate: 0.06,
  amort_years: 30,
  target_dscr: 1.25,
  max_ltv: 0.75,
  min_debt_yield: 0.085,
};

const CONSTRAINT_LABELS: Record<string, string> = {
  dscr: 'DSCR',
  ltv: 'LTV',
  debt_yield: 'Debt Yield',
};

function AgencySizingPanel() {
  const [req, setReq] = useState<AgencySizingRequest>(AGENCY_DEFAULTS);
  const { result, loading, error } = useLiveCalc(recalcAgencySizing, req);
  const r: AgencySizingResponse | null = result;

  const set = (patch: Partial<AgencySizingRequest>) => setReq((prev) => ({ ...prev, ...patch }));

  const constraints = [
    { label: 'By DSCR', key: 'dscr', value: r?.by_dscr ?? null },
    { label: 'By LTV', key: 'ltv', value: r?.by_ltv ?? null },
    { label: 'By Debt Yield', key: 'debt_yield', value: r?.by_debt_yield ?? null },
  ];

  return (
    <Card className="p-6 flex flex-col">
      <div className="flex items-center justify-between mb-1">
        <h3 className="text-lg font-head font-semibold text-slate flex items-center">
          <Building2 className="w-5 h-5 mr-2 text-teal" /> Agency Takeout Sizing
        </h3>
        <StatusLine loading={loading} error={error} />
      </div>
      <p className="text-xs text-slate/50 mb-5">
        Max loan is the LOWEST of the three constraints (the binding one).
      </p>

      {/* result */}
      <div className={`mb-5 ${loading ? 'opacity-60' : ''}`}>
        <div className="flex items-end gap-3">
          <span className="font-head font-bold text-4xl text-teal tnum">
            {r?.max_loan != null ? fmtUSD(r.max_loan) : '—'}
          </span>
          {r?.binding_constraint && (
            <Badge tone="teal" className="mb-1.5">
              binding: {CONSTRAINT_LABELS[r.binding_constraint] ?? r.binding_constraint}
            </Badge>
          )}
        </div>
        <div className="mt-3 divide-y divide-slate/10 text-sm">
          {constraints.map((c) => {
            const isBinding = r?.binding_constraint === c.key && c.value != null;
            return (
              <div key={c.key} className="flex items-center justify-between py-1.5">
                <span className={isBinding ? 'font-semibold text-teal' : 'text-slate/70'}>
                  {c.label}
                </span>
                <span className={`tnum ${isBinding ? 'font-semibold text-teal' : 'text-slate'}`}>
                  {c.value != null ? fmtUSD(c.value) : '—'}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {/* inputs */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-auto">
        <NumField
          label="Stabilized NOI"
          kind="usd"
          value={req.stabilized_noi}
          onCommit={(v) => v != null && set({ stabilized_noi: v })}
        />
        <NumField
          label="Stabilized Value"
          kind="usd"
          value={req.stabilized_value}
          onCommit={(v) => v != null && set({ stabilized_value: v })}
        />
        <NumField
          label="Refi Rate"
          kind="pct"
          value={req.refi_rate}
          onCommit={(v) => v != null && set({ refi_rate: v })}
        />
        <NumField
          label="Amortization (Years)"
          kind="int"
          value={req.amort_years}
          onCommit={(v) => v != null && set({ amort_years: v })}
        />
        <NumField
          label="Target DSCR"
          kind="ratio"
          value={req.target_dscr}
          onCommit={(v) => v != null && set({ target_dscr: v })}
        />
        <NumField
          label="Max LTV"
          kind="pct"
          value={req.max_ltv}
          onCommit={(v) => v != null && set({ max_ltv: v })}
        />
        <NumField
          label="Min Debt Yield"
          kind="pct"
          value={req.min_debt_yield}
          onCommit={(v) => v != null && set({ min_debt_yield: v })}
        />
      </div>
    </Card>
  );
}

// ===========================================================================
// Page
// ===========================================================================

export function BondScreen() {
  // key-bump remount resets all three panels to their defaults
  const [resetKey, setResetKey] = useState(0);

  return (
    <div className="space-y-8">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <h1 className="text-3xl font-head font-bold text-slate-near flex items-center gap-2">
              <Landmark className="w-7 h-7 text-teal" /> Bond Screen
            </h1>
            <Badge tone="taupe">EFB</Badge>
            <Badge tone="electric">Live Recalc</Badge>
          </div>
          <div className="flex flex-wrap items-center text-slate/60 text-sm gap-4">
            <span>501(c)(3) / EFB tax-exempt bond sizing on stabilized NOI</span>
            <span className="flex items-center">
              <Activity className="w-4 h-4 mr-1" /> Deterministic engine · no LLM
            </span>
          </div>
        </div>
        <Button variant="secondary" icon={RotateCcw} onClick={() => setResetKey((k) => k + 1)}>
          Reset
        </Button>
      </div>

      <EFBSizingPanel key={`efb-${resetKey}`} />

      <div className="pt-2 border-t border-slate/10">
        <h2 className="eyebrow text-slate/60 mb-4">Companion Calculators</h2>
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6 items-stretch">
          <ExitCapPanel key={`exit-${resetKey}`} />
          <AgencySizingPanel key={`agency-${resetKey}`} />
        </div>
      </div>

      <div className="flex items-start gap-2 text-xs text-slate/60 bg-teal-panel/50 rounded-lg p-3 border border-teal/15">
        <Info className="w-4 h-4 mt-0.5 shrink-0 text-teal" />
        <p>
          All figures computed by the validated deterministic engine via{' '}
          <code className="font-mono">/api/underwrite/efb</code>,{' '}
          <code className="font-mono">/api/recalc/exit-cap</code> and{' '}
          <code className="font-mono">/api/recalc/agency-sizing</code>. No LLM is involved in any
          number on this page. Property-tax exemption is display color only; it never changes the
          bond sizing math.
        </p>
      </div>
    </div>
  );
}
