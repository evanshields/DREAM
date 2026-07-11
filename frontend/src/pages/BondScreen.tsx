import { useEffect, useMemo, useRef, useState } from 'react';
import {
  Landmark,
  Activity,
  RefreshCw,
  RotateCcw,
  TrendingUp,
  Crosshair,
  Building2,
  Info,
  CheckCircle2,
  AlertTriangle,
} from 'lucide-react';
import {
  underwriteEFB,
  recalcExitCap,
  recalcAgencySizing,
  ApiError,
  type EFBUnderwriteRequest,
  type EFBHeadlineMetrics,
  type ExitCapRequest,
  type ExitCapResponse,
  type ExitCapStrategy,
  type AgencySizingRequest,
  type AgencySizingResponse,
} from '../lib/api';
import { Card, Button, Badge } from '../components/ui';
import { fmtUSD, fmtUSDFull, fmtPct, fmtEM } from '../lib/format';

// ---------------------------------------------------------------------------
// Bond Screen — deterministic 501(c)(3)/EFB tax-exempt bond sizing.
// Three LLM-free endpoints (backend/routers/recalc.py):
//   POST /api/underwrite/efb      — size bonds to a target DSCR on stabilized NOI
//   POST /api/recalc/exit-cap     — 3-method exit-cap triangulation (takes HIGHEST)
//   POST /api/recalc/agency-sizing — takeout loan = MIN(DSCR, LTV, debt-yield)
// Defaults mirror the backend request models exactly.
// ---------------------------------------------------------------------------

// --- edit helpers (same pattern as AssumptionDashboard) --------------------

type Kind = 'usd' | 'pct' | 'int' | 'ratio';

function displayValue(kind: Kind, v: number | null | undefined): string {
  if (v == null) return '—';
  if (kind === 'usd') return fmtUSD(v);
  if (kind === 'pct') return fmtPct(v);
  if (kind === 'ratio') return fmtEM(v);
  return `${v}`;
}

function toEditString(kind: Kind, v: number | null | undefined): string {
  if (v == null) return '';
  if (kind === 'pct') return (v * 100).toString();
  return v.toString();
}

// '' -> null (field cleared); invalid -> undefined (ignore the commit)
function fromEditString(kind: Kind, s: string): number | null | undefined {
  if (s.trim() === '') return null;
  const n = Number(s);
  if (!Number.isFinite(n)) return undefined;
  if (kind === 'pct') return n / 100;
  if (kind === 'int') return Math.round(n);
  return n;
}

// --- shared live-calc hook: run once immediately, then debounce 450ms ------

interface LiveCalcState<Res> {
  result: Res | null;
  loading: boolean;
  error: string | null;
}

function useLiveCalc<Req, Res>(
  fn: (req: Req, signal?: AbortSignal) => Promise<Res>,
  req: Req,
): LiveCalcState<Res> {
  const [result, setResult] = useState<Res | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);
  const debounceRef = useRef<number | null>(null);
  const firstRef = useRef(true);

  useEffect(() => {
    const run = () => {
      abortRef.current?.abort();
      const ctrl = new AbortController();
      abortRef.current = ctrl;
      setLoading(true);
      setError(null);
      fn(req, ctrl.signal)
        .then((res) => {
          if (ctrl.signal.aborted) return;
          setResult(res);
          setLoading(false);
        })
        .catch((e: unknown) => {
          if (ctrl.signal.aborted) return;
          if (e instanceof ApiError && e.status === 401) return;
          setError(e instanceof Error ? e.message : String(e));
          setLoading(false);
        });
    };
    if (firstRef.current) {
      firstRef.current = false;
      run();
    } else {
      if (debounceRef.current) window.clearTimeout(debounceRef.current);
      debounceRef.current = window.setTimeout(run, 450);
    }
  }, [fn, req]);

  // abort in-flight + cancel pending debounce on unmount only
  useEffect(
    () => () => {
      abortRef.current?.abort();
      if (debounceRef.current) window.clearTimeout(debounceRef.current);
    },
    [],
  );

  return { result, loading, error };
}

// --- status line (recalculating / error / up to date) ----------------------

function StatusLine({ loading, error }: { loading: boolean; error: string | null }) {
  return (
    <div className="h-5 flex items-center">
      {loading ? (
        <span className="inline-flex items-center text-xs font-medium text-teal">
          <RefreshCw className="w-3.5 h-3.5 mr-1.5 animate-spin" /> recalculating…
        </span>
      ) : error ? (
        <span className="inline-flex items-center text-xs font-medium text-danger">
          <AlertTriangle className="w-3.5 h-3.5 mr-1.5" /> {error}
        </span>
      ) : (
        <span className="inline-flex items-center text-xs font-medium text-ok">
          <CheckCircle2 className="w-3.5 h-3.5 mr-1.5" /> up to date
        </span>
      )}
    </div>
  );
}

// --- generic numeric field (draft-buffered; commits on blur/Enter) ---------

interface NumFieldProps {
  label: string;
  kind: Kind;
  value: number | null;
  hint?: string;
  optional?: boolean;
  onCommit: (v: number | null) => void;
}

function NumField({ label, kind, value, hint, optional, onCommit }: NumFieldProps) {
  const [draft, setDraft] = useState<string | null>(null);

  const commit = (raw: string) => {
    const parsed = fromEditString(kind, raw);
    setDraft(null);
    if (parsed === undefined) return; // unparseable, keep prior value
    if (parsed === null && !optional) return; // required field cleared, keep prior value
    onCommit(parsed);
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-1.5">
        <label className="text-sm font-semibold text-slate">{label}</label>
        <Badge tone="neutral">{kind === 'pct' ? '%' : kind === 'usd' ? 'USD' : kind === 'ratio' ? 'x' : '#'}</Badge>
      </div>
      <div className="flex items-center gap-2">
        <input
          className="input"
          type="number"
          step={kind === 'pct' ? '0.01' : kind === 'ratio' ? '0.01' : kind === 'int' ? '1' : '1000'}
          placeholder={optional ? 'optional' : undefined}
          value={draft ?? toEditString(kind, value)}
          onChange={(e) => setDraft(e.target.value)}
          onBlur={(e) => commit(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') (e.target as HTMLInputElement).blur();
          }}
          aria-label={label}
        />
        <span className="text-xs text-slate/50 whitespace-nowrap min-w-[56px] text-right tnum">
          {displayValue(kind, value)}
        </span>
      </div>
      {hint && <p className="text-[11px] text-slate/50 mt-1 leading-tight">{hint}</p>}
    </div>
  );
}

// ===========================================================================
// EFB bond sizing (primary panel)
// ===========================================================================

// Backend EFBUnderwriteRequest defaults; stabilized_noi has no backend default,
// so we seed a representative workforce-housing NOI as the starting point.
const EFB_DEFAULTS: EFBUnderwriteRequest = {
  stabilized_noi: 2_500_000,
  target_dscr: 1.15,
  bond_rate: 0.05,
  amortization_years: 35,
  annual_property_tax_exempted: null,
  hold_years: 10,
};

function EFBPanel() {
  const [req, setReq] = useState<EFBUnderwriteRequest>(EFB_DEFAULTS);
  const { result, loading, error } = useLiveCalc(underwriteEFB, req);
  const hm: EFBHeadlineMetrics | null = result?.headline_metrics ?? null;

  const set = (patch: Partial<EFBUnderwriteRequest>) => setReq((prev) => ({ ...prev, ...patch }));

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
        label: `Tax Savings (${req.hold_years}-Yr)`,
        value: hm?.tax_savings_10yr != null ? fmtUSD(hm.tax_savings_10yr) : '—',
        sub:
          hm?.tax_savings_10yr != null
            ? 'Property tax exempted over the hold'
            : 'Enter annual property tax exempted to compute',
      },
    ],
    [hm, req.hold_years],
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="eyebrow text-slate/60 flex items-center">
          <TrendingUp className="w-4 h-4 mr-2" /> Bond Sizing
        </h2>
        <StatusLine loading={loading} error={error} />
      </div>

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

      <EFBPanel key={`efb-${resetKey}`} />

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
