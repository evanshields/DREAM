import { useCallback, useEffect, useRef, useState } from 'react';
import { Badge, Button, Card, Spinner } from '../ui';
import { Details, ProblemList } from './MonoEvidence';
import { monoJobTerminal } from '../../hooks/useMonoJob';
import { monthLabel } from './MonoResults';
import { cancelMonoPublication, downloadMonoPublication, getMonoPublications, monoError, publishMono,
  revisionOf, type MonoDeliverable, type MonoDownloadFormat, type MonoPublications as PublicationState,
  type MonoView } from '../../lib/monoApi';

const downloads: { kind: MonoDeliverable; format: MonoDownloadFormat; label: string; filename: string }[] = [
  { kind: 'package', format: 'archive', label: 'All files', filename: 'underwriting-package.zip' },
  { kind: 'memo', format: 'pdf', label: 'Memo', filename: 'memo.pdf' },
  { kind: 'onepager', format: 'pdf', label: 'One-pager', filename: 'onepager.pdf' },
  { kind: 'deck', format: 'editable', label: 'Editable presentation', filename: 'deck.pptx' },
  { kind: 'workbook', format: 'workbook', label: 'Excel workbook', filename: 'mono.xlsx' },
];

export function MonoPublications({ view }: { view: MonoView }) {
  const [state, setState] = useState<PublicationState | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState<string | null>(null);
  const active = useRef(true);
  const generation = useRef(0);
  const actionBusy = useRef(false);
  const request = useRef<{ fingerprint: string; key: string } | null>(null);
  const dealId = view.deal_id;
  const reload = useCallback(async (signal?: AbortSignal) => {
    const expected = ++generation.current;
    try {
      const next = await getMonoPublications(dealId, signal);
      if (!active.current || signal?.aborted || expected !== generation.current || next.deal_id !== dealId) return;
      setState((previous) => previous && previous.revision > next.revision ? previous : next);
      setError(null);
    } catch (failure) {
      if (active.current && !signal?.aborted && expected === generation.current) setError(monoError(failure));
    }
  }, [dealId]);

  useEffect(() => {
    active.current = true;
    const controller = new AbortController();
    let timer: ReturnType<typeof setTimeout>;
    const poll = async () => {
      await reload(controller.signal);
      if (!controller.signal.aborted) timer = setTimeout(() => { void poll(); }, 5000);
    };
    void poll();
    return () => { active.current = false; controller.abort(); clearTimeout(timer); generation.current += 1; };
  }, [reload, view.revision, view.current_result?.result_id, view.gates.comps?.event_id, view.gates.go_no_go?.event_id]);

  const current = !error && state?.revision === view.revision ? state.current : null;
  const selected = view.current_result?.selected_financial_projection;
  const historical = selected?.provider_id === 'esplanade_historical_annual_v1';
  const comparisonMonth = selected?.historical_profile?.comparison_month;
  const visibleDownloads = downloads.map((item) => historical ? {
    ...item,
    label: item.kind === 'workbook' ? `Historical source comparison: ${monthLabel(comparisonMonth)} (Excel)` : item.label,
    filename: `historical-source-comparison-${comparisonMonth}-${item.filename}`,
  } : item);
  const running = state?.jobs.filter((job) => !monoJobTerminal(job.state)) ?? [];
  const perform = async (name: string, action: () => Promise<void>) => {
    if (actionBusy.current) return;
    actionBusy.current = true;
    setBusy(name); setError(null);
    generation.current += 1;
    try { await action(); }
    catch (failure) { if (active.current) setError(monoError(failure)); }
    finally { actionBusy.current = false; if (active.current) setBusy(null); }
  };

  const build = () => perform('build', async () => {
    const fingerprint = JSON.stringify([revisionOf(view), view.current_result?.result_id,
      view.gates.comps?.event_id, view.gates.go_no_go?.event_id]);
    if (request.current?.fingerprint !== fingerprint) request.current = { fingerprint, key: crypto.randomUUID() };
    await publishMono(dealId, { ...revisionOf(view), idempotency_key: request.current!.key });
    request.current = null;
    await reload();
  });

  const download = (item: typeof downloads[number]) => perform(item.label, async () => {
    if (!current) return;
    const blob = await downloadMonoPublication(dealId, current.job_id, item.kind, item.format);
    if (!active.current) return;
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url; anchor.download = item.filename;
    document.body.appendChild(anchor); anchor.click(); anchor.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  });

  return <Card className="p-5 space-y-4" aria-label="Underwriting documents">
    <div className="flex flex-wrap gap-4 items-center justify-between"><div><h2 className="text-xl">Underwriting documents</h2>
      <p className="text-sm text-slate/60 mt-1">Build the memo, one-pager, presentation and Excel workbook together from one reviewed result.</p></div>
      <Button disabled={Boolean(busy) || Boolean(error) || running.length > 0 || !state?.can_publish || state.revision !== view.revision}
        onClick={() => { void build(); }}>{busy === 'build' && <Spinner />}Build all four files</Button></div>
    {!state && !error && <p className="text-sm flex gap-2"><Spinner />Checking document readiness…</p>}
    {error && <p role="alert" className="text-sm text-danger">{error}</p>}
    <ProblemList values={state?.blocking_reasons ?? []} />
    <ProblemList values={state?.warnings ?? []} />
    {running.map((job) => <div key={job.job_id} className="rounded-lg bg-offwhite p-4 space-y-2" role="status">
      <div className="flex flex-wrap items-center gap-3"><Spinner /><strong>Documents {job.state}</strong><Badge tone="teal">Revision {job.revision}</Badge>
        <Button variant="secondary" disabled={Boolean(busy) || job.cancel_requested}
          onClick={() => { void perform('cancel', async () => { await cancelMonoPublication(dealId, job.job_id); await reload(); }); }}>
          {job.cancel_requested ? 'Cancellation requested' : 'Request cancellation'}</Button></div>
      {job.revision !== view.revision && <p className="text-sm text-warn">An earlier revision is being built. Its files will remain historical.</p>}
      <ol className="text-sm text-slate/70 list-decimal pl-5">{job.steps.map((step) => <li key={step}>{step}</li>)}</ol>
      <p className="text-xs text-slate/60">You can leave and return. Progress is saved on the server.</p></div>)}
    {current && <div className="space-y-3"><div className="flex flex-wrap gap-2 items-center"><Badge tone="ok">Current package verified</Badge>
      <span className="text-xs text-slate/60">Revision {current.revision}. Built {new Date(current.updated_at).toLocaleString()}.</span></div>
      {historical && <p className="text-sm text-slate/70">Historical source comparison: {monthLabel(comparisonMonth)}. Expected closing: {monthLabel(selected?.historical_profile?.expected_closing_month)}, day unknown. Annual source periods and conventions apply. Open Historical Bond for the selected comparison.</p>}
      <div className="flex flex-wrap gap-2">{visibleDownloads.map((item) => <Button key={item.kind} variant="secondary"
        disabled={Boolean(busy)} onClick={() => { void download(item); }}>{busy === item.label && <Spinner />}{item.label}</Button>)}</div>
      <p className="text-xs text-slate/60">The complete package includes private underwriting records. Sharing requires separate authorization.</p></div>}
    {state && state.jobs.length > 0 && <Details title="Document history"><div className="space-y-3">{[...state.jobs].reverse().map((job) =>
      <div key={job.job_id} className="border-t border-slate/10 pt-3 text-sm"><div className="flex gap-2 flex-wrap items-center">
        <strong>Revision {job.revision}</strong><Badge tone={job.is_current ? 'ok' : 'taupe'}>{job.is_current ? 'Current' : monoJobTerminal(job.state) ? 'Historical' : 'In progress'}</Badge>
        <span>{job.state}</span></div><p className="text-xs text-slate/60 mt-1">{job.created_at ? new Date(job.created_at).toLocaleString() : ''}</p>
        <ProblemList values={job.diagnostics} /></div>)}</div></Details>}
  </Card>;
}
