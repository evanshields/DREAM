import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import {
  SlidersHorizontal,
  RefreshCw,
  TrendingUp,
  Activity,
  BarChart3,
  RotateCcw,
  Info,
  CheckCircle2,
  AlertTriangle,
} from 'lucide-react';
import {
  LineChart,
  Line,
  ResponsiveContainer,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
} from 'recharts';
import {
  type ACQRecalcRequest,
  type HeadlineMetrics,
  type SweepField,
  type SweepMetric,
  recalc,
  sensitivity,
  ApiError,
} from '../lib/api';
import { Card, Button, Badge } from './ui';
import { fmtUSD, fmtEM } from '../lib/format';

// Esplanade-validated ACQ defaults (the oracle deal). Mirrors backend
// tests/test_engine_boundary_esplanade.py + gemini_ui ESPLANADE_DEFAULTS.
export const ESPLANADE_DEFAULTS: ACQRecalcRequest = {
  bridge_loan: 23800000,
  bridge_rate: 0.08,
  bridge_io_years: 2,
  refi_loan: 31944864,
  refi_rate: 0.06,
  refi_io_years: 3,
  refi_amort_years: 30,
  refi_year: 2,
  total_equity: 13145673,
  noi_series: [
    2387932, 2563041, 2742167, 2883487, 2983197, 3134540, 3241781, 3352240, 3466013, 3583198,
  ],
  exit_cap: 0.06,
  sale_year: 7,
  costs_of_sale: 0.02,
  servicing_spread: 0.0116,
  refi_cost_pct: 0.02,
  exit_on_forward_noi: true,
  years: 10,
};

type FieldKey =
  | 'bridge_loan'
  | 'bridge_rate'
  | 'bridge_io_years'
  | 'refi_loan'
  | 'refi_rate'
  | 'refi_io_years'
  | 'refi_amort_years'
  | 'refi_year'
  | 'total_equity'
  | 'exit_cap'
  | 'sale_year'
  | 'costs_of_sale'
  | 'servicing_spread'
  | 'refi_cost_pct';

type Kind = 'usd' | 'pct' | 'int';
type Group = 'Bridge Debt' | 'Refinance / Takeout' | 'Equity & Exit' | 'Costs & Spreads';

interface FieldMeta {
  key: FieldKey;
  label: string;
  kind: Kind;
  range: string;
  benchmark: string;
  source: string;
  group: Group;
}

const FIELD_META: FieldMeta[] = [
  { key: 'bridge_loan', label: 'Bridge Loan', kind: 'usd', range: '$15M – $40M', benchmark: '~65% of cost', source: 'Esplanade S&U', group: 'Bridge Debt' },
  { key: 'bridge_rate', label: 'Bridge Rate', kind: 'pct', range: '7.0% – 10.0%', benchmark: 'SOFR + 350', source: 'Term sheet', group: 'Bridge Debt' },
  { key: 'bridge_io_years', label: 'Bridge I/O Years', kind: 'int', range: '1 – 3 yrs', benchmark: '2 yrs', source: 'Bridge terms', group: 'Bridge Debt' },
  { key: 'refi_loan', label: 'Refi / Takeout Loan', kind: 'usd', range: '$25M – $40M', benchmark: '≤75% LTV', source: 'Agency sizing', group: 'Refinance / Takeout' },
  { key: 'refi_rate', label: 'Refi Rate', kind: 'pct', range: '5.0% – 7.0%', benchmark: 'Tsy + 150', source: 'Agency quote', group: 'Refinance / Takeout' },
  { key: 'refi_io_years', label: 'Refi I/O Years', kind: 'int', range: '0 – 5 yrs', benchmark: '3 yrs', source: 'Agency terms', group: 'Refinance / Takeout' },
  { key: 'refi_amort_years', label: 'Refi Amortization', kind: 'int', range: '25 – 35 yrs', benchmark: '30 yrs', source: 'Agency terms', group: 'Refinance / Takeout' },
  { key: 'refi_year', label: 'Refi Year', kind: 'int', range: '1 – 4', benchmark: 'Year 2', source: 'Business plan', group: 'Refinance / Takeout' },
  { key: 'total_equity', label: 'Total Equity', kind: 'usd', range: '$10M – $20M', benchmark: 'Gap to cost', source: 'Esplanade S&U', group: 'Equity & Exit' },
  { key: 'exit_cap', label: 'Exit Cap', kind: 'pct', range: '5.0% – 7.0%', benchmark: 'Going-in + 25bps', source: 'Triangulation', group: 'Equity & Exit' },
  { key: 'sale_year', label: 'Sale Year', kind: 'int', range: '5 – 10', benchmark: 'Year 7', source: 'Hold strategy', group: 'Equity & Exit' },
  { key: 'costs_of_sale', label: 'Costs of Sale', kind: 'pct', range: '1.5% – 3.0%', benchmark: '2.0%', source: 'Std disposition', group: 'Costs & Spreads' },
  { key: 'servicing_spread', label: 'Servicing Spread', kind: 'pct', range: '0.5% – 1.5%', benchmark: '116 bps', source: 'Agency servicing', group: 'Costs & Spreads' },
  { key: 'refi_cost_pct', label: 'Refi Cost %', kind: 'pct', range: '1.5% – 2.5%', benchmark: '2.0%', source: 'Closing costs', group: 'Costs & Spreads' },
];

const GROUPS: Group[] = ['Bridge Debt', 'Refinance / Takeout', 'Equity & Exit', 'Costs & Spreads'];

const fmtPctLocal = (v: number) => `${(v * 100).toFixed(2)}%`;

function displayValue(kind: Kind, v: number): string {
  if (kind === 'usd') return fmtUSD(v);
  if (kind === 'pct') return fmtPctLocal(v);
  return `${v}`;
}
function toEditString(kind: Kind, v: number): string {
  if (kind === 'pct') return (v * 100).toString();
  return v.toString();
}
function fromEditString(kind: Kind, s: string): number | null {
  if (s.trim() === '') return null;
  const n = Number(s);
  if (!Number.isFinite(n)) return null;
  if (kind === 'pct') return n / 100;
  if (kind === 'int') return Math.round(n);
  return n;
}

const METRIC_META: Record<
  SweepMetric,
  { label: string; fmt: (v: number) => string; target?: number; targetLabel?: string }
> = {
  irr: { label: 'IRR', fmt: (v) => `${(v * 100).toFixed(1)}%`, target: 0.15, targetLabel: 'Target 15%' },
  equity_multiple: { label: 'Equity Multiple', fmt: fmtEM, target: 1.8, targetLabel: 'Target 1.8x' },
  coc_stabilized: { label: 'Cash-on-Cash (Stab.)', fmt: (v) => `${(v * 100).toFixed(1)}%`, target: 0.07, targetLabel: 'Target 7%' },
  exit_value: { label: 'Exit Value', fmt: (v) => fmtUSD(v) },
};

const SWEEP_FIELDS: { key: SweepField; label: string; kind: Kind }[] = [
  { key: 'exit_cap', label: 'Exit Cap', kind: 'pct' },
  { key: 'refi_rate', label: 'Refi Rate', kind: 'pct' },
  { key: 'bridge_rate', label: 'Bridge Rate', kind: 'pct' },
  { key: 'servicing_spread', label: 'Servicing Spread', kind: 'pct' },
  { key: 'costs_of_sale', label: 'Costs of Sale', kind: 'pct' },
  { key: 'total_equity', label: 'Total Equity', kind: 'usd' },
  { key: 'refi_loan', label: 'Refi Loan', kind: 'usd' },
  { key: 'bridge_loan', label: 'Bridge Loan', kind: 'usd' },
];

function buildSweepValues(kind: Kind, base: number, steps = 9): number[] {
  let lo: number, hi: number;
  if (kind === 'pct') {
    lo = Math.max(0.0001, base - 0.015);
    hi = base + 0.015;
  } else {
    lo = base * 0.8;
    hi = base * 1.2;
  }
  const out: number[] = [];
  for (let i = 0; i < steps; i++) out.push(lo + ((hi - lo) * i) / (steps - 1));
  return out;
}

export function AssumptionDashboard({ seed }: { seed?: ACQRecalcRequest }) {
  const initial = useMemo(() => ({ ...ESPLANADE_DEFAULTS, ...(seed ?? {}) }), [seed]);
  const [assumptions, setAssumptions] = useState<ACQRecalcRequest>(initial);
  const [drafts, setDrafts] = useState<Record<string, string>>({});
  const [metrics, setMetrics] = useState<HeadlineMetrics | null>(null);
  const [recalculating, setRecalculating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const debounceRef = useRef<number | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  const runRecalc = useCallback((payload: ACQRecalcRequest) => {
    abortRef.current?.abort();
    const ctrl = new AbortController();
    abortRef.current = ctrl;
    setRecalculating(true);
    setError(null);
    recalc(payload, ctrl.signal)
      .then((res) => {
        setMetrics(res.headline_metrics);
        setRecalculating(false);
      })
      .catch((e: unknown) => {
        if (ctrl.signal.aborted) return;
        if (e instanceof ApiError && e.status === 401) return;
        setError(e instanceof Error ? e.message : String(e));
        setRecalculating(false);
      });
  }, []);

  useEffect(() => {
    runRecalc(initial);
    return () => abortRef.current?.abort();
  }, [runRecalc, initial]);

  const commitField = useCallback(
    (meta: FieldMeta, raw: string) => {
      const parsed = fromEditString(meta.kind, raw);
      if (parsed === null) return;
      setAssumptions((prev) => {
        const next = { ...prev, [meta.key]: parsed };
        if (debounceRef.current) window.clearTimeout(debounceRef.current);
        debounceRef.current = window.setTimeout(() => runRecalc(next), 450);
        return next;
      });
    },
    [runRecalc],
  );

  const resetAll = useCallback(() => {
    setDrafts({});
    setAssumptions(initial);
    if (debounceRef.current) window.clearTimeout(debounceRef.current);
    runRecalc(initial);
  }, [runRecalc, initial]);

  const headlineTiles = useMemo(() => {
    const m = metrics;
    return [
      { key: 'irr', meta: METRIC_META.irr, value: m?.irr },
      { key: 'equity_multiple', meta: METRIC_META.equity_multiple, value: m?.equity_multiple },
      { key: 'coc_stabilized', meta: METRIC_META.coc_stabilized, value: m?.coc_stabilized },
      { key: 'exit_value', meta: METRIC_META.exit_value, value: m?.exit_value },
    ] as const;
  }, [metrics]);

  return (
    <div className="space-y-8">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <h2 className="text-2xl font-head font-bold text-teal">Assumption Dashboard</h2>
            <Badge tone="electric">Live Recalc</Badge>
          </div>
          <div className="flex flex-wrap items-center text-slate/60 text-sm gap-4">
            <span className="flex items-center">
              <SlidersHorizontal className="w-4 h-4 mr-1" /> ACQ assumptions — edit any value
            </span>
            <span className="flex items-center">
              <Activity className="w-4 h-4 mr-1" /> Deterministic engine · no LLM
            </span>
          </div>
        </div>
        <Button variant="secondary" icon={RotateCcw} onClick={resetAll}>
          Reset
        </Button>
      </div>

      {/* Headline metrics */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h3 className="eyebrow text-slate/60 flex items-center">
            <TrendingUp className="w-4 h-4 mr-2" /> Headline Returns
          </h3>
          <div className="h-5 flex items-center">
            {recalculating ? (
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
        </div>

        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {headlineTiles.map(({ key, meta, value }) => {
            const hasVal = typeof value === 'number';
            const onTarget = hasVal && meta.target != null ? (value as number) >= meta.target : null;
            return (
              <Card
                key={key}
                className={`p-5 flex flex-col justify-between h-full border-t-4 border-t-teal ${
                  recalculating ? 'opacity-60' : ''
                }`}
              >
                <span className="eyebrow text-slate/50">{meta.label}</span>
                <div className="mt-2">
                  <span className="text-3xl font-head font-bold text-slate-near tnum">
                    {hasVal ? meta.fmt(value as number) : '—'}
                  </span>
                </div>
                <div
                  className={`mt-2 text-xs font-medium flex items-center ${
                    onTarget == null ? 'text-slate/50' : onTarget ? 'text-ok' : 'text-warn'
                  }`}
                >
                  {meta.targetLabel ? (
                    <>
                      {onTarget != null && <TrendingUp className="w-3 h-3 mr-1" />}
                      {meta.targetLabel}
                    </>
                  ) : (
                    'Sale value (gross)'
                  )}
                </div>
              </Card>
            );
          })}
        </div>
      </div>

      {/* Editable assumption cards */}
      <div className="space-y-6">
        <h3 className="eyebrow text-slate/60 flex items-center">
          <SlidersHorizontal className="w-4 h-4 mr-2" /> Assumptions
          <span className="ml-2 normal-case font-normal text-xs text-slate/50">
            — edit any value; returns recalc automatically
          </span>
        </h3>

        {GROUPS.map((group) => (
          <div key={group}>
            <h4 className="text-xs font-semibold text-slate mb-3 uppercase tracking-wider font-label">
              {group}
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {FIELD_META.filter((f) => f.group === group).map((meta) => {
                const current = assumptions[meta.key] as number;
                const draftKey = meta.key;
                const draftVal =
                  draftKey in drafts ? drafts[draftKey] : toEditString(meta.kind, current);
                return (
                  <Card key={meta.key} className="p-4">
                    <div className="flex items-start justify-between mb-2">
                      <span className="text-sm font-semibold text-slate">{meta.label}</span>
                      <Badge tone="neutral">
                        {meta.kind === 'pct' ? '%' : meta.kind === 'usd' ? 'USD' : '#'}
                      </Badge>
                    </div>
                    <div className="flex items-center gap-2 mb-3">
                      <input
                        className="input"
                        type="number"
                        step={meta.kind === 'pct' ? '0.01' : meta.kind === 'int' ? '1' : '1000'}
                        value={draftVal}
                        onChange={(e) => setDrafts((d) => ({ ...d, [draftKey]: e.target.value }))}
                        onBlur={(e) => {
                          commitField(meta, e.target.value);
                          setDrafts((d) => {
                            const { [draftKey]: _omit, ...rest } = d;
                            return rest;
                          });
                        }}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') (e.target as HTMLInputElement).blur();
                        }}
                        aria-label={meta.label}
                      />
                      <span className="text-xs text-slate/50 whitespace-nowrap min-w-[64px] text-right tnum">
                        {displayValue(meta.kind, current)}
                      </span>
                    </div>
                    <dl className="space-y-1 text-[11px] leading-tight">
                      <div className="flex justify-between">
                        <dt className="text-slate/50">Range</dt>
                        <dd className="text-slate font-medium">{meta.range}</dd>
                      </div>
                      <div className="flex justify-between">
                        <dt className="text-slate/50">Benchmark</dt>
                        <dd className="text-slate font-medium">{meta.benchmark}</dd>
                      </div>
                      <div className="flex justify-between">
                        <dt className="text-slate/50">Source</dt>
                        <dd className="text-slate font-medium">{meta.source}</dd>
                      </div>
                    </dl>
                  </Card>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      <SensitivityPanel base={assumptions} />

      <div className="flex items-start gap-2 text-xs text-slate/60 bg-teal-panel/50 rounded-lg p-3 border border-teal/15">
        <Info className="w-4 h-4 mt-0.5 shrink-0 text-teal" />
        <p>
          All figures computed by the validated deterministic engine via{' '}
          <code className="font-mono">/api/recalc</code>. No LLM is involved in any number on this
          page. Range and benchmark values are advisory context only — the engine is the source of
          truth.
        </p>
      </div>
    </div>
  );
}

function SensitivityPanel({ base }: { base: ACQRecalcRequest }) {
  const [field, setField] = useState<SweepField>('exit_cap');
  const [metric, setMetric] = useState<SweepMetric>('irr');
  const [data, setData] = useState<{ x: number; xLabel: string; y: number | null }[]>([]);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  const fieldKind = useMemo<Kind>(
    () => SWEEP_FIELDS.find((f) => f.key === field)?.kind ?? 'pct',
    [field],
  );

  const run = useCallback(() => {
    const baseVal = base[field] as number;
    const values = buildSweepValues(fieldKind, baseVal);
    abortRef.current?.abort();
    const ctrl = new AbortController();
    abortRef.current = ctrl;
    setLoading(true);
    setErr(null);
    sensitivity({ base, field, values, metric }, ctrl.signal)
      .then((res) => {
        setData(
          res.grid.map((p) => ({
            x: p.value,
            xLabel: fieldKind === 'pct' ? `${(p.value * 100).toFixed(2)}%` : fmtUSD(p.value),
            y: p.result,
          })),
        );
        setLoading(false);
      })
      .catch((e: unknown) => {
        if (ctrl.signal.aborted) return;
        if (e instanceof ApiError && e.status === 401) return;
        setErr(e instanceof Error ? e.message : String(e));
        setLoading(false);
      });
  }, [base, field, fieldKind, metric]);

  useEffect(() => {
    run();
    return () => abortRef.current?.abort();
  }, [run]);

  const mMeta = METRIC_META[metric];
  const baseVal = base[field] as number;

  return (
    <Card className="p-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 mb-5">
        <h3 className="text-lg font-head font-semibold text-slate flex items-center">
          <BarChart3 className="w-5 h-5 mr-2 text-teal" /> Sensitivity Grid
        </h3>
        <div className="flex flex-wrap items-center gap-2">
          <label className="text-xs text-slate/60">Field</label>
          <select
            value={field}
            onChange={(e) => setField(e.target.value as SweepField)}
            className="h-9 rounded-md border border-slate/20 bg-white px-3 text-sm text-slate focus:outline-none focus:ring-2 focus:ring-teal"
          >
            {SWEEP_FIELDS.map((f) => (
              <option key={f.key} value={f.key}>
                {f.label}
              </option>
            ))}
          </select>
          <label className="text-xs text-slate/60 ml-2">Metric</label>
          <select
            value={metric}
            onChange={(e) => setMetric(e.target.value as SweepMetric)}
            className="h-9 rounded-md border border-slate/20 bg-white px-3 text-sm text-slate focus:outline-none focus:ring-2 focus:ring-teal"
          >
            {(Object.keys(METRIC_META) as SweepMetric[]).map((k) => (
              <option key={k} value={k}>
                {METRIC_META[k].label}
              </option>
            ))}
          </select>
          <Button variant="secondary" icon={RefreshCw} onClick={run}>
            Re-sweep
          </Button>
        </div>
      </div>

      <div className="h-5 mb-2">
        {loading ? (
          <span className="inline-flex items-center text-xs font-medium text-teal">
            <RefreshCw className="w-3.5 h-3.5 mr-1.5 animate-spin" /> recalculating…
          </span>
        ) : err ? (
          <span className="inline-flex items-center text-xs font-medium text-danger">
            <AlertTriangle className="w-3.5 h-3.5 mr-1.5" /> {err}
          </span>
        ) : (
          <span className="text-xs text-slate/50">
            Sweeping{' '}
            <b className="text-slate">{SWEEP_FIELDS.find((f) => f.key === field)?.label}</b> · holding
            all else fixed · {data.length} points
          </span>
        )}
      </div>

      <div className={`w-full h-80 ${loading ? 'opacity-60' : ''}`}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 10, right: 24, left: 8, bottom: 8 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#3C485620" />
            <XAxis
              dataKey="xLabel"
              tick={{ fontSize: 11, fill: '#3C4856' }}
              stroke="#3C485640"
              interval="preserveStartEnd"
            />
            <YAxis
              tick={{ fontSize: 11, fill: '#3C4856' }}
              stroke="#3C485640"
              tickFormatter={(v: number) => mMeta.fmt(v)}
              width={70}
            />
            <Tooltip
              formatter={(v: number) => [mMeta.fmt(v), mMeta.label]}
              labelFormatter={(l) =>
                `${SWEEP_FIELDS.find((f) => f.key === field)?.label}: ${l}`
              }
              contentStyle={{ fontSize: 12, borderRadius: 8 }}
            />
            {mMeta.target != null && (
              <ReferenceLine
                y={mMeta.target}
                stroke="#16A34A"
                strokeDasharray="4 4"
                label={{
                  value: mMeta.targetLabel,
                  position: 'insideTopRight',
                  fontSize: 10,
                  fill: '#16A34A',
                }}
              />
            )}
            <ReferenceLine
              x={fieldKind === 'pct' ? `${(baseVal * 100).toFixed(2)}%` : fmtUSD(baseVal)}
              stroke="#005253"
              strokeDasharray="2 2"
              label={{ value: 'base', position: 'insideTop', fontSize: 10, fill: '#005253' }}
            />
            <Line
              type="monotone"
              dataKey="y"
              name={mMeta.label}
              stroke="#005253"
              strokeWidth={2.5}
              dot={{ r: 3, fill: '#005253' }}
              activeDot={{ r: 5 }}
              connectNulls
              isAnimationActive={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="mt-4 overflow-x-auto">
        <table className="w-full text-sm text-center">
          <thead>
            <tr className="text-xs text-slate/60 bg-teal-panel/60">
              <th className="py-2 px-3 rounded-l text-left">
                {SWEEP_FIELDS.find((f) => f.key === field)?.label}
              </th>
              <th className="py-2 px-3 rounded-r">{mMeta.label}</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate/10">
            {data.map((d, i) => {
              const isBase = Math.abs(d.x - baseVal) < Math.abs(baseVal || 1) * 1e-6;
              return (
                <tr
                  key={i}
                  className={isBase ? 'bg-teal/5 font-semibold' : 'hover:bg-teal-panel/40 transition-colors'}
                >
                  <td className={`py-1.5 px-3 text-left tnum ${isBase ? 'text-teal' : 'text-slate'}`}>
                    {d.xLabel}
                    {isBase && <span className="ml-2 text-[10px] uppercase text-slate/50">base</span>}
                  </td>
                  <td className={`py-1.5 px-3 tnum ${isBase ? 'text-teal' : 'text-slate'}`}>
                    {d.y == null ? '—' : mMeta.fmt(d.y)}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </Card>
  );
}
