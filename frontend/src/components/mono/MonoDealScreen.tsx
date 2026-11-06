import { useCallback, useEffect, useRef, useState } from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';
import { Badge, Button, Card, Spinner } from '../ui';
import { calculateMono, getMonoDeal, monoConflict, monoError, revisionOf, type MonoJob, type MonoView } from '../../lib/monoApi';
import { monoJobTerminal, useMonoJob } from '../../hooks/useMonoJob';
import { MonoAssumptions } from './MonoAssumptions';
import { Details, ProblemList } from './MonoEvidence';
import { MonoHumanReview, MonoNarrative } from './MonoHumanReview';
import { MonoIdentityDetails, MonoResultView, MonoRunHistory } from './MonoResults';
import { MonoPublications } from './MonoPublications';

function activeJob(jobs: MonoJob[]): MonoJob | null {
  return jobs.filter((job) => !monoJobTerminal(job.state)).sort((a, b) => b.created_at.localeCompare(a.created_at))[0] ?? null;
}

function Screen({ dealId }: { dealId: string }) {
  const [view, setView] = useState<MonoView | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [calculating, setCalculating] = useState(false);
  const [selectedJob, setSelectedJob] = useState<MonoJob | null>(null);
  const [tab, setTab] = useState<'assumptions' | 'review' | 'history'>('assumptions');
  const requestVersion = useRef(0);
  const mounted = useRef(true);
  const loadController = useRef<AbortController | null>(null);
  const calculationRequest = useRef<{ fingerprint: string; key: string } | null>(null);
  const calculationInFlight = useRef(false);

  const accept = useCallback((next: MonoView) => {
    if (!mounted.current || next.deal_id !== dealId) return;
    // A delayed read must never undo an accepted edit or newer server revision.
    setView((previous) => previous && previous.revision > next.revision ? previous : next);
  }, [dealId]);

  const reload = useCallback(async () => {
    const version = ++requestVersion.current;
    loadController.current?.abort();
    const controller = new AbortController();
    loadController.current = controller;
    try {
      const next = await getMonoDeal(dealId, controller.signal);
      if (!mounted.current || version !== requestVersion.current || controller.signal.aborted) return;
      if (next.contract_version !== 1) throw new Error('This Mono response version is not supported.');
      accept(next);
      setSelectedJob((previous) => activeJob(next.jobs) ?? (previous ? next.jobs.find((job) => job.job_id === previous.job_id) ?? null : null));
      setError(null);
    } catch (failure) {
      if (controller.signal.aborted || !mounted.current || version !== requestVersion.current) return;
      setError(monoError(failure));
      throw failure;
    } finally { if (mounted.current && version === requestVersion.current) setLoading(false); }
  }, [dealId, accept]);

  useEffect(() => {
    mounted.current = true;
    void reload().catch(() => undefined);
    return () => { mounted.current = false; requestVersion.current += 1; loadController.current?.abort(); };
  }, [reload]);

  const terminal = useCallback(() => { void reload().catch(() => undefined); }, [reload]);
  const progress = useMonoJob(dealId, selectedJob, terminal);
  const running = Boolean(progress.job && !monoJobTerminal(progress.job.state));

  const saved = (next: MonoView) => {
    requestVersion.current += 1;
    loadController.current?.abort();
    accept(next);
    setError(null);
  };

  const calculate = async () => {
    if (!view || calculationInFlight.current) return;
    calculationInFlight.current = true;
    const revision = revisionOf(view);
    const fingerprint = JSON.stringify(revision);
    if (calculationRequest.current?.fingerprint !== fingerprint) {
      calculationRequest.current = { fingerprint, key: crypto.randomUUID() };
    }
    setCalculating(true); setActionError(null);
    try {
      const job = await calculateMono(dealId, { ...revision, idempotency_key: calculationRequest.current!.key });
      calculationRequest.current = null;
      if (!mounted.current || job.deal_id !== dealId) return;
      setSelectedJob(job);
      // The job receipt is not a current result. Only the next validated deal
      // view can promote output values into the current result panel.
      void reload().catch(() => undefined);
    } catch (failure) {
      if (!mounted.current) return;
      setActionError(monoConflict(failure)?.message ?? monoError(failure));
    } finally { calculationInFlight.current = false; if (mounted.current) setCalculating(false); }
  };

  if (!view) return <Card className="p-8" aria-busy={loading}>
    {loading ? <p className="flex items-center gap-2"><Spinner />Loading registered Mono deal…</p> : <div className="space-y-3"><p role="alert" className="text-danger">{error || 'The registered Mono deal could not be loaded.'}</p><Button variant="secondary" onClick={() => { setLoading(true); void reload().catch(() => undefined); }}>Try again</Button></div>}
  </Card>;

  return <div className="space-y-7 animate-fade" data-mono-revision={view.revision}>
    <Card className="p-5 sm:p-6 border-t-4 border-t-teal">
      <div className="flex flex-wrap items-start justify-between gap-5"><div><p className="eyebrow text-teal">Mono underwriting</p><h1 className="text-3xl sm:text-4xl mt-2">{view.name}</h1><div className="flex gap-2 flex-wrap items-center mt-3"><Badge tone="teal">Revision {view.revision}</Badge><Badge tone={view.current_result ? 'ok' : 'warn'}>{view.current_result ? 'Current calculation verified' : 'No current calculation'}</Badge><Badge tone={view.readiness.ready ? 'ok' : 'warn'}>{view.readiness.ready ? 'Evidence ready' : 'Evidence incomplete'}</Badge></div></div>
        <div className="flex flex-wrap gap-2"><Button variant="secondary" icon={RefreshCw} onClick={() => { void reload().catch(() => undefined); }}>Refresh</Button><Button disabled={!view.can_edit || calculating || running} onClick={() => { void calculate(); }}>{calculating && <Spinner />}{running ? 'Calculation in progress' : 'Recalculate revision'}</Button></div>
      </div>
      <p className="text-sm text-slate/60 mt-4">Review inputs, calculate, then make an explicit human decision. Missing evidence remains visible.</p>
      {!view.can_edit && <p className="text-xs text-slate/60 mt-2">Viewing only. Editing and calculation require authorized authenticated access.</p>}
      <div className="mt-4"><MonoIdentityDetails identity={view.identity} /></div>
    </Card>

    {(error || actionError) && <div role="alert" className="rounded-lg border border-danger/25 bg-danger/5 p-4 space-y-2"><p className="text-sm text-danger">{actionError || error}</p><Button variant="secondary" onClick={() => { setActionError(null); void reload().catch(() => undefined); }}>Reread server state</Button></div>}

    {progress.job && <Card className="p-5 space-y-3" aria-label="Calculation progress">
      <div className="flex flex-wrap items-center justify-between gap-3"><div className="flex flex-wrap gap-2 items-center">{running && <Spinner />}<h2 className="text-xl">Calculation {progress.job.state}</h2><Badge tone={progress.job.revision === view.revision ? 'teal' : 'taupe'}>Revision {progress.job.revision}</Badge></div><p className="text-sm tnum" aria-label="Calculation elapsed time">{progress.elapsed} seconds elapsed</p></div>
      <p className="text-xs break-all text-slate/60">Job {progress.job.job_id}</p>
      {progress.job.revision !== view.revision && <p className="text-sm text-warn">This job uses an earlier revision. Its completion will remain historical.</p>}
      <div role="status" aria-live="polite" className="text-sm text-slate/70">{progress.cancelPending ? 'Cancellation requested. Waiting for a terminal server receipt.' : running ? 'You can leave and return. The server retains this job and the screen reconnects from the deal record.' : 'Terminal status recorded. Refresh the deal to see the validated current result.'}</div>
      {progress.connectionError && <p role="alert" className="text-sm text-warn">Connection interrupted: {progress.connectionError}. Reconnecting automatically.</p>}
      <div className="flex gap-2 flex-wrap">{running && <Button variant="secondary" disabled={!view.can_edit || progress.cancelPending} onClick={() => { void progress.cancel(); }}>Request cancellation</Button>}<Button variant="ghost" onClick={progress.reconnect}>Reconnect job</Button></div>
      <ProblemList values={progress.job.warnings} /><ProblemList values={progress.job.diagnostics} />
    </Card>}

    <section aria-label="Current calculator outputs" className="space-y-4"><div className="flex flex-wrap gap-3 items-center justify-between"><h2 className="text-2xl">Current outputs</h2><span className="text-xs text-slate/60">Revision {view.revision}</span></div>
      {view.current_result ? <MonoResultView result={view.current_result} /> : <Card className="p-5 flex gap-3"><AlertTriangle className="w-5 h-5 text-warn shrink-0" /><div><p className="font-semibold text-sm">No verified result for this revision</p><p className="text-sm text-slate/60 mt-1">Calculate the saved inputs to produce a new result. Earlier results remain in calculation history.</p></div></Card>}
    </section>

    <Card className="p-5 space-y-4"><div><h2 className="text-xl">Evidence readiness</h2><p className="text-sm text-slate/60 mt-1">These are distinct counts. Diagnostic messages can refer to the same field.</p></div><div className="grid sm:grid-cols-3 gap-3">{[
      ['Recorded bucket D', view.readiness.recorded_d_count],
      ['Unique unverified fields', view.readiness.unverified_field_count],
      ['Diagnostic messages', view.readiness.diagnostic_count],
    ].map(([label, value]) => <div key={label} className="p-3 rounded-lg bg-offwhite"><p className="text-xs text-slate/60">{label}</p><p className="text-2xl tnum text-teal mt-1">{value}</p></div>)}</div><Details title={`Readiness diagnostics (${view.readiness.problems.length})`} open={!view.readiness.ready}><ProblemList values={view.readiness.problems} empty="No readiness diagnostics recorded." /></Details></Card>

    <MonoPublications view={view} />

    <nav aria-label="Mono deal sections" className="flex gap-1 border-b border-slate/15 overflow-x-auto">{([
      ['assumptions', 'Assumptions'], ['review', 'Human review'], ['history', 'Calculation history'],
    ] as const).map(([id, label]) => <button key={id} type="button" aria-current={tab === id ? 'page' : undefined} onClick={() => setTab(id)} className={`px-4 py-3 text-sm font-semibold whitespace-nowrap border-b-2 focus-visible:outline-teal ${tab === id ? 'border-teal text-teal' : 'border-transparent text-slate/60 hover:text-teal'}`}>{label}</button>)}</nav>
    <div hidden={tab !== 'assumptions'}><MonoAssumptions view={view} onSaved={saved} onReread={reload} /></div>
    <div hidden={tab !== 'review'} className="space-y-6"><MonoHumanReview view={view} onSaved={saved} onReread={reload} /><MonoNarrative view={view} /></div>
    <div hidden={tab !== 'history'}><MonoRunHistory jobs={view.jobs} /></div>
  </div>;
}

// Remount on deal change so unsaved entries, gates and old requests cannot leak
// from one deal into another, even when a parent reuses the same page instance.
export function MonoDealScreen({ dealId }: { dealId: string }) {
  return <Screen key={dealId} dealId={dealId} />;
}
