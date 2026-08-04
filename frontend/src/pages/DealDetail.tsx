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
  LayoutDashboard,
  FileText,
  History,
  FileSpreadsheet,
  type LucideIcon,
} from 'lucide-react';
import {
  getDeal,
  ApiError,
  type JobView,
  type DealFullView,
  type DealHeadlineMetrics,
  type DealMemoBlock,
  type EFBHeadlineMetrics,
  type EFBUnderwriteRequest,
  type ACQRecalcRequest,
  type OpenQuestion,
} from '../lib/api';
import { Card, Badge, statusTone } from '../components/ui';
import { AssumptionDashboard } from '../components/AssumptionDashboard';
import {
  EFBMetricTiles,
  EFBSizingPanel,
  EFB_SIZING_DEFAULTS,
} from '../components/EFBMetricTiles';
import { DealMemo } from '../components/DealMemo';
import { DealTimeline } from '../components/DealTimeline';
import { DealRail } from '../components/DealRail';
import { DealExport } from '../components/DealExport';
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

// ---------------------------------------------------------------------------
// ACQ dashboard seeding. spec.engine_inputs is an OPAQUE bag (only present on deals
// underwritten after input-capture shipped) — never trust its shape. pickACQSeed type-guards
// every known ACQRecalcRequest key with the correct runtime type before copying it.
// ---------------------------------------------------------------------------

// numeric scalar ACQRecalcRequest keys we accept from engine_inputs (arrays handled separately).
const ACQ_NUMBER_KEYS = [
  'bridge_loan',
  'bridge_rate',
  'bridge_io_years',
  'refi_loan',
  'refi_rate',
  'refi_io_years',
  'refi_amort_years',
  'refi_year',
  'total_equity',
  'exit_cap',
  'sale_year',
  'costs_of_sale',
  'servicing_spread',
  'refi_cost_pct',
  'years',
] as const;

// number[] series keys.
const ACQ_SERIES_KEYS = [
  'noi_series',
  'gpr_series',
  'egi_series',
  'opex_series',
  'vacancy_series',
  'debt_service',
] as const;

const isNumberArray = (v: unknown): v is number[] =>
  Array.isArray(v) && v.every((n) => typeof n === 'number' && Number.isFinite(n));

// Copy ONLY the keys whose runtime type matches; ignore everything else in the opaque bag.
function pickACQSeed(engineInputs: Record<string, unknown>): Partial<ACQRecalcRequest> {
  const seed: Partial<ACQRecalcRequest> = {};
  for (const k of ACQ_NUMBER_KEYS) {
    const v = engineInputs[k];
    if (typeof v === 'number' && Number.isFinite(v)) {
      (seed as Record<string, unknown>)[k] = v;
    }
  }
  for (const k of ACQ_SERIES_KEYS) {
    const v = engineInputs[k];
    if (isNumberArray(v)) {
      (seed as Record<string, unknown>)[k] = v;
    }
  }
  if (typeof engineInputs.exit_on_forward_noi === 'boolean') {
    seed.exit_on_forward_noi = engineInputs.exit_on_forward_noi;
  }
  return seed;
}

// The tab strip: Overview (CP-1 metrics + gates + live modelling), Memo (LLM deal memo),
// Activity (audit trail), Export (App -> Excel push).
type TabId = 'overview' | 'memo' | 'activity' | 'export';
const TABS: { id: TabId; label: string; icon: LucideIcon }[] = [
  { id: 'overview', label: 'Overview', icon: LayoutDashboard },
  { id: 'memo', label: 'Memo', icon: FileText },
  { id: 'activity', label: 'Activity', icon: History },
  { id: 'export', label: 'Export', icon: FileSpreadsheet },
];

// The CP-1 review + assumption dashboard (PRD §4.4).
// Two arrival paths:
//   1. From the underwrite flow -> location.state.job carries the full CP-1 JobView
//      (spec + headline_metrics + gate_summary + open_questions).
//   2. Cold load (pipeline click / refresh) -> GET /api/deals/{id} carries the full view
//      (spec + gate_summary + latest job block), so gates/questions/memo survive a refresh.
export function DealDetail() {
  const { id } = useParams<{ id: string }>();
  const location = useLocation();
  const stateJob = (location.state as { job?: JobView } | null)?.job ?? null;

  const [deal, setDeal] = useState<DealFullView | null>(null);
  const [loading, setLoading] = useState(!stateJob);
  const [error, setError] = useState<string | null>(null);

  const [tab, setTab] = useState<TabId>('overview');
  // Activity fetches on first visit and stays mounted after (tab switches just hide it).
  const [auditVisited, setAuditVisited] = useState(false);
  useEffect(() => {
    if (tab === 'activity') setAuditVisited(true);
  }, [tab]);
  // Bumped when the Overview rail adds/removes a note or task so the (already-mounted) Activity
  // timeline re-fetches to include it.
  const [timelineRefresh, setTimelineRefresh] = useState(0);

  useEffect(() => {
    // If we already have the CP-1 job from navigation, this fetch is non-blocking color
    // (name/status/persisted memo). On a cold load it's the primary source.
    if (!id) return;
    let cancelled = false;
    getDeal(id)
      .then((d) => {
        if (cancelled) return;
        setDeal(d);
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

  // Gates + open questions: fresh CP-1 job view first, then the persisted deal view
  // (spec.qa + the latest job block), so cold loads keep them.
  const gateSummary = useMemo<Record<string, unknown> | null>(() => {
    if (stateJob?.gate_summary) return stateJob.gate_summary;
    if (deal?.gate_summary && Object.keys(deal.gate_summary).length > 0) return deal.gate_summary;
    return null;
  }, [stateJob, deal]);
  const openQuestions = stateJob?.open_questions ?? deal?.job?.open_questions ?? [];

  // The persisted memo rides at spec.narrative.memo (POST /memo writes it there).
  // Prefer the persisted deal spec (it reflects any memo generated after CP-1) over the
  // navigation job's CP-1 snapshot.
  const specMemo = useMemo<DealMemoBlock | null>(() => {
    const spec = (deal?.spec ?? stateJob?.spec) as
      | { narrative?: { memo?: { markdown?: unknown; generated_at?: unknown } } }
      | undefined;
    const m = spec?.narrative?.memo;
    if (m && typeof m.markdown === 'string') {
      return {
        markdown: m.markdown,
        generated_at: typeof m.generated_at === 'string' ? m.generated_at : '',
      };
    }
    return null;
  }, [deal, stateJob]);

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

  // Seed the ACQ assumption dashboard from THIS deal's underwrite. Two tiers:
  //   full    — spec.engine_inputs present (deals underwritten after input-capture shipped):
  //             the exact validated debt terms, type-guarded via pickACQSeed.
  //   partial — pre-existing deals lack engine_inputs; recover what we can (total_equity +
  //             noi_series from headline metrics, exit_cap + sale_year from
  //             spec.meta.critical_inputs) and let the dashboard fill the rest with Esplanade
  //             defaults. The caption tells the user which case they're looking at.
  const acqSeed = useMemo<{ seed: Partial<ACQRecalcRequest> | undefined; full: boolean }>(() => {
    if (isEFB) return { seed: undefined, full: false };

    const spec = (deal?.spec ?? stateJob?.spec) as Record<string, unknown> | undefined;

    // Tier 1 — full validated inputs captured on the deal.
    const engineInputs = spec?.engine_inputs;
    if (engineInputs && typeof engineInputs === 'object' && !Array.isArray(engineInputs)) {
      const seed = pickACQSeed(engineInputs as Record<string, unknown>);
      return { seed, full: true };
    }

    // Tier 2 — partial recovery for deals that predate input capture.
    const seed: Partial<ACQRecalcRequest> = {};

    if (headline) {
      if (typeof headline.total_equity === 'number' && Number.isFinite(headline.total_equity))
        seed.total_equity = headline.total_equity;
      if (isNumberArray(headline.noi_series)) seed.noi_series = headline.noi_series;
    }

    // exit_cap + sale_year come off the intake critical_inputs (sale_year from hold_years).
    const meta = spec?.meta as { critical_inputs?: Record<string, unknown> } | undefined;
    const ci = meta?.critical_inputs;
    if (ci && typeof ci === 'object') {
      if (typeof ci.exit_cap === 'number' && Number.isFinite(ci.exit_cap)) seed.exit_cap = ci.exit_cap;
      if (typeof ci.hold_years === 'number' && Number.isFinite(ci.hold_years))
        seed.sale_year = ci.hold_years;
    }

    // nothing recoverable → let the dashboard run pure Esplanade defaults (undefined seed).
    return Object.keys(seed).length ? { seed, full: false } : { seed: undefined, full: false };
  }, [isEFB, deal, stateJob, headline]);

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

      {/* Tab strip: Overview / Memo / Activity / Export */}
      <div className="flex gap-1 border-b border-slate/10" role="tablist">
        {TABS.map((t) => (
          <button
            key={t.id}
            role="tab"
            aria-selected={tab === t.id}
            onClick={() => setTab(t.id)}
            className={`inline-flex items-center gap-1.5 px-4 py-2.5 text-sm font-medium border-b-2 -mb-px transition-colors ${
              tab === t.id
                ? 'border-teal text-teal'
                : 'border-transparent text-slate/50 hover:text-slate-near'
            }`}
          >
            <t.icon className="w-4 h-4" /> {t.label}
          </button>
        ))}
      </div>

      {tab === 'overview' && (
        <div className="grid grid-cols-1 lg:grid-cols-[minmax(0,1fr)_20rem] gap-6 items-start">
          <div className="space-y-8 min-w-0">
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
          computed metrics); ACQ keeps the full assumption dashboard (seeded from the deal's
          captured engine inputs, or partially from headline metrics + intake for older deals). */}
      <div className="pt-2 border-t border-slate/10">
        {isEFB ? (
          <EFBSizingPanel seed={efbSeed} />
        ) : (
          <>
            {acqSeed.seed && (
              <p className="text-xs text-slate/50 mb-3">
                {acqSeed.full
                  ? 'Seeded from this deal’s underwrite'
                  : 'Partially seeded. Debt terms show Esplanade defaults (deal predates input capture).'}
              </p>
            )}
            <AssumptionDashboard seed={acqSeed.seed} />
          </>
        )}
      </div>
          </div>

          {/* Right rail — deal team + tasks + notes (Phase 5). Sticky on wide screens; stacks
              below the main content on narrow ones. */}
          {id && (
            <aside className="lg:sticky lg:top-6">
              <DealRail dealId={id} onChanged={() => setTimelineRefresh((n) => n + 1)} />
            </aside>
          )}
        </div>
      )}

      {tab === 'memo' && id && <DealMemo dealId={id} dealName={dealName} memo={specMemo} />}

      {/* Activity mounts on first visit and stays mounted (hidden) so the fetch isn't repeated. */}
      {auditVisited && id && (
        <div className={tab === 'activity' ? '' : 'hidden'}>
          <DealTimeline dealId={id} refreshKey={timelineRefresh} />
        </div>
      )}

      {tab === 'export' && id && <DealExport dealId={id} />}
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
                ) : typeof v === 'object' && v !== null ? (
                  // a metric row with no pass/fail verdict (e.g. unit_count reconciliation counts):
                  // show a neutral badge, keep the raw payload in a tooltip rather than dumping JSON
                  <span title={JSON.stringify(v)}>
                    <Badge tone="neutral">
                      <MinusCircle className="w-3 h-3" /> Recorded
                    </Badge>
                  </span>
                ) : (
                  <span className="text-xs text-slate/50 font-mono max-w-[50%] truncate">
                    {String(v)}
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
