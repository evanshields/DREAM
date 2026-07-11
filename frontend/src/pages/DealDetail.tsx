import { useState, useEffect, useMemo } from 'react';
import { useParams, useLocation, Link } from 'react-router-dom';
import {
  ArrowLeft,
  TrendingUp,
  Layers,
  DollarSign,
  Landmark,
  ShieldCheck,
  ShieldAlert,
  HelpCircle,
  CheckCircle2,
  XCircle,
  MinusCircle,
  Loader2,
  AlertTriangle,
} from 'lucide-react';
import {
  listDeals,
  ApiError,
  type JobView,
  type DealListItem,
  type DealHeadlineMetrics,
  type EFBHeadlineMetrics,
  type EFBUnderwriteRequest,
  type OpenQuestion,
} from '../lib/api';
import { Card, Badge, statusTone } from '../components/ui';
import { AssumptionDashboard } from '../components/AssumptionDashboard';
import {
  EFBMetricTiles,
  EFBSizingPanel,
  EFB_SIZING_DEFAULTS,
} from '../components/EFBMetricTiles';
import { fmtUSD, fmtPct1, fmtEM, prettyStatus, fmtDate } from '../lib/format';

// Pull the EFB metric keys out of the generic per-deal headline_metrics bag.
const EFB_METRIC_KEYS = [
  'bond_amount',
  'annual_debt_service',
  'maximum_debt_service',
  'year1_noi',
  'year1_dscr',
  'target_dscr',
  'bond_rate',
  'tax_savings_10yr',
] as const;

function pickEFBMetrics(hm: DealHeadlineMetrics): Partial<EFBHeadlineMetrics> {
  const out: Partial<EFBHeadlineMetrics> = {};
  for (const k of EFB_METRIC_KEYS) {
    const v = hm[k];
    if (typeof v === 'number') out[k] = v;
  }
  return out;
}

// The CP-1 review + assumption dashboard (PRD §4.4).
// Two arrival paths:
//   1. From the underwrite flow -> location.state.job carries the full CP-1 JobView
//      (spec + headline_metrics + gate_summary + open_questions).
//   2. Cold load (pipeline click / refresh) -> we fetch the deal from GET /api/deals
//      for its headline_metrics. (There's no single-deal GET endpoint by contract; the
//      live recalc dashboard is fully functional regardless.)
export function DealDetail() {
  const { id } = useParams<{ id: string }>();
  const location = useLocation();
  const stateJob = (location.state as { job?: JobView } | null)?.job ?? null;

  const [deal, setDeal] = useState<DealListItem | null>(null);
  const [loading, setLoading] = useState(!stateJob);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // If we already have the CP-1 job from navigation, we still fetch the deal index for
    // name/status; but it's non-blocking. On a cold load it's the primary source.
    let cancelled = false;
    listDeals()
      .then((deals) => {
        if (cancelled) return;
        setDeal(deals.find((d) => d.deal_id === id) ?? null);
        setLoading(false);
      })
      .catch((e) => {
        if (cancelled) return;
        if (e instanceof ApiError && e.status === 401) return;
        setError(e instanceof Error ? e.message : String(e));
        setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [id, stateJob]);

  // Headline metrics: prefer the fresh job view, fall back to the deal index.
  const headline: DealHeadlineMetrics | null = useMemo(() => {
    if (stateJob?.headline_metrics) return stateJob.headline_metrics;
    if (deal?.headline_metrics && Object.keys(deal.headline_metrics).length > 0)
      return deal.headline_metrics;
    return null;
  }, [stateJob, deal]);

  const dealName = stateJob?.spec
    ? ((stateJob.spec as { meta?: { deal_name?: string } }).meta?.deal_name ?? 'Deal')
    : (deal?.deal_name ?? 'Deal');
  const routing = stateJob?.routing ?? deal?.routing ?? 'ACQ';
  const isEFB = routing === 'EFB';
  const status = stateJob?.status ?? deal?.status ?? '';

  const gateSummary = stateJob?.gate_summary ?? null;
  const openQuestions = stateJob?.open_questions ?? [];

  // Seed the live EFB sizing panel from the deal's computed headline metrics.
  const efbSeed = useMemo<Partial<EFBUnderwriteRequest> | undefined>(() => {
    if (!isEFB || !headline) return undefined;
    const m = pickEFBMetrics(headline);
    const seed: Partial<EFBUnderwriteRequest> = {};
    if (m.year1_noi != null) seed.stabilized_noi = m.year1_noi;
    if (m.target_dscr != null) seed.target_dscr = m.target_dscr;
    if (m.bond_rate != null) seed.bond_rate = m.bond_rate;
    // headline exposes only the hold-total savings (tax_savings_10yr, keyed to
    // the 10-yr default hold) — back out the annual figure for the panel input.
    if (m.tax_savings_10yr != null)
      seed.annual_property_tax_exempted = m.tax_savings_10yr / EFB_SIZING_DEFAULTS.hold_years;
    return seed;
  }, [isEFB, headline]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-24 text-slate/50">
        <Loader2 className="w-6 h-6 animate-spin mr-2" /> Loading deal…
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div>
        <Link
          to="/pipeline"
          className="inline-flex items-center gap-1.5 text-sm text-slate/60 hover:text-teal mb-3"
        >
          <ArrowLeft className="w-4 h-4" /> Pipeline
        </Link>
        <div className="flex flex-wrap items-center gap-3">
          <h1 className="text-3xl font-head font-bold text-slate-near">{dealName}</h1>
          <Badge tone={routing === 'EFB' ? 'taupe' : 'teal'}>{routing}</Badge>
          {status && <Badge tone={statusTone(status)}>{prettyStatus(status)}</Badge>}
        </div>
        {deal && (
          <p className="text-xs text-slate/40 mt-1">Updated {fmtDate(deal.updated_at)}</p>
        )}
      </div>

      {error && (
        <Card className="p-4 border-danger/30 bg-danger/5">
          <div className="flex items-center gap-2 text-danger text-sm">
            <AlertTriangle className="w-4 h-4" /> {error}
          </div>
        </Card>
      )}

      {/* CP-1: headline metrics (routing-aware — EFB shows bond sizing tiles) */}
      {headline ? (
        isEFB ? (
          <div>
            <h2 className="eyebrow text-slate/60 mb-3 flex items-center">
              <Landmark className="w-4 h-4 mr-2" /> CP-1 Headline Metrics
            </h2>
            <EFBMetricTiles hm={pickEFBMetrics(headline)} />
          </div>
        ) : (
          <HeadlineMetricsBlock hm={headline} />
        )
      ) : (
        <Card className="p-5 bg-teal-panel/40 border-teal/15">
          <p className="text-sm text-slate/70">
            No computed metrics on file for this deal yet. Use the live dashboard below to model it,
            or run a fresh{' '}
            <Link to="/underwrite" className="text-teal underline">
              underwrite
            </Link>
            .
          </p>
        </Card>
      )}

      {/* Gate summary (only available from a fresh CP-1 job view) */}
      {gateSummary && <GateSummaryBlock gates={gateSummary} />}

      {/* Open questions (LLM-inferred cells to confirm; non-blocking) */}
      {openQuestions.length > 0 && <OpenQuestionsBlock questions={openQuestions} />}

      {/* Live modelling — EFB gets the bond sizing panel (seeded from the deal's
          computed metrics); ACQ keeps the full assumption dashboard. */}
      <div className="pt-2 border-t border-slate/10">
        {isEFB ? <EFBSizingPanel seed={efbSeed} /> : <AssumptionDashboard />}
      </div>
    </div>
  );
}

function HeadlineMetricsBlock({ hm }: { hm: DealHeadlineMetrics }) {
  const tiles = [
    {
      label: 'IRR',
      value: typeof hm.irr === 'number' ? fmtPct1(hm.irr) : '—',
      icon: TrendingUp,
    },
    {
      label: 'Equity Multiple',
      value: typeof hm.equity_multiple === 'number' ? fmtEM(hm.equity_multiple) : '—',
      icon: Layers,
    },
    {
      label: 'CoC (Stabilized)',
      value: typeof hm.coc_stabilized === 'number' ? fmtPct1(hm.coc_stabilized) : '—',
      icon: DollarSign,
    },
    {
      label: 'Exit Value',
      value: typeof hm.exit_value === 'number' ? fmtUSD(hm.exit_value) : '—',
      icon: DollarSign,
    },
  ];
  return (
    <div>
      <h2 className="eyebrow text-slate/60 mb-3 flex items-center">
        <TrendingUp className="w-4 h-4 mr-2" /> CP-1 Headline Metrics
      </h2>
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {tiles.map((t) => (
          <Card key={t.label} className="p-5 border-t-4 border-t-teal">
            <span className="eyebrow text-slate/50 flex items-center gap-1">
              <t.icon className="w-3 h-3" /> {t.label}
            </span>
            <div className="font-head font-bold text-4xl text-teal tnum mt-2">{t.value}</div>
          </Card>
        ))}
      </div>
    </div>
  );
}

function GateSummaryBlock({ gates }: { gates: Record<string, unknown> }) {
  const entries = Object.entries(gates);
  if (entries.length === 0) return null;

  // {skipped: true, reason} — e.g. formula_audit on EFB runs. Neutral, not a failure.
  const gateSkipped = (v: unknown): string | null => {
    if (v && typeof v === 'object') {
      const o = v as Record<string, unknown>;
      if (o.skipped === true) return typeof o.reason === 'string' ? o.reason : '';
    }
    return null;
  };

  const gatePassed = (v: unknown): boolean | null => {
    if (typeof v === 'boolean') return v;
    if (v && typeof v === 'object') {
      const o = v as Record<string, unknown>;
      if (typeof o.passed === 'boolean') return o.passed;
      if (typeof o.pass === 'boolean') return o.pass;
      if (typeof o.ok === 'boolean') return o.ok;
      if (typeof o.status === 'string') return o.status.toLowerCase() === 'pass';
    }
    if (typeof v === 'string') return v.toLowerCase() === 'pass' || v.toLowerCase() === 'ok';
    return null;
  };

  const anyFail = entries.some(
    ([, v]) => gateSkipped(v) === null && gatePassed(v) === false,
  );

  return (
    <div>
      <h2 className="eyebrow text-slate/60 mb-3 flex items-center">
        {anyFail ? (
          <ShieldAlert className="w-4 h-4 mr-2 text-danger" />
        ) : (
          <ShieldCheck className="w-4 h-4 mr-2 text-ok" />
        )}
        Gate Summary
      </h2>
      <Card className="p-1">
        <ul className="divide-y divide-slate/10">
          {entries.map(([name, v]) => {
            const skippedReason = gateSkipped(v);
            const passed = gatePassed(v);
            return (
              <li key={name} className="flex items-center justify-between gap-3 px-4 py-3">
                <span className="text-sm font-medium text-slate font-mono">{name}</span>
                {skippedReason !== null ? (
                  <span
                    className="flex items-center gap-2 min-w-0"
                    title={skippedReason || undefined}
                  >
                    {skippedReason && (
                      <span className="text-xs text-slate/50 truncate max-w-[280px]">
                        {skippedReason}
                      </span>
                    )}
                    <Badge tone="neutral" className="shrink-0">
                      <MinusCircle className="w-3 h-3" /> Skipped
                    </Badge>
                  </span>
                ) : passed === true ? (
                  <Badge tone="ok">
                    <CheckCircle2 className="w-3 h-3" /> Pass
                  </Badge>
                ) : passed === false ? (
                  <Badge tone="danger">
                    <XCircle className="w-3 h-3" /> Fail
                  </Badge>
                ) : (
                  <span className="text-xs text-slate/50 font-mono max-w-[50%] truncate">
                    {typeof v === 'object' ? JSON.stringify(v) : String(v)}
                  </span>
                )}
              </li>
            );
          })}
        </ul>
      </Card>
    </div>
  );
}

function OpenQuestionsBlock({ questions }: { questions: OpenQuestion[] }) {
  return (
    <div>
      <h2 className="eyebrow text-slate/60 mb-3 flex items-center">
        <HelpCircle className="w-4 h-4 mr-2" /> Open Questions
        <span className="ml-2 normal-case font-normal text-xs text-slate/50">
          — review at CP-1 (non-blocking)
        </span>
      </h2>
      <Card className="p-1">
        <ul className="divide-y divide-slate/10">
          {questions.map((q) => (
            <li key={q.id} className="px-4 py-3">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="text-sm text-slate font-medium">{q.question}</p>
                  <p className="text-xs text-slate/40 font-mono mt-0.5">
                    {q.field}
                    {q.current_value != null && (
                      <> · current: {String(q.current_value)}</>
                    )}
                  </p>
                </div>
                <Badge tone={q.source === 'cited' ? 'teal' : 'warn'}>
                  {q.source === 'cited' ? 'Cited' : 'LLM-inferred'}
                </Badge>
              </div>
            </li>
          ))}
        </ul>
      </Card>
    </div>
  );
}
