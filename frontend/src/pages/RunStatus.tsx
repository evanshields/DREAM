// Read-only run status and evidence view. List at /runs, detail at /runs/:id.
// No forms, no buttons that change anything. Reads frozen sample runs only.
import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { Card, Spinner } from '../components/ui';
import {
  EventTimeline,
  EvidenceList,
  GateList,
  HeadlineList,
  HoldList,
  StateBadge,
  StateBanner,
} from '../components/runstatus/RunStatusParts';
import { getRunStatus, listRunStatus, type RunSummary, type RunView } from '../lib/runStatusApi';

type Load<T> = { kind: 'loading' } | { kind: 'error'; message: string } | { kind: 'ok'; data: T };

function useLoad<T>(fn: (signal: AbortSignal) => Promise<T>, key: string): Load<T> {
  const [state, setState] = useState<Load<T>>({ kind: 'loading' });
  useEffect(() => {
    const ctl = new AbortController();
    setState({ kind: 'loading' });
    fn(ctl.signal)
      .then((data) => setState({ kind: 'ok', data }))
      .catch((e: unknown) => {
        if (ctl.signal.aborted) return;
        setState({ kind: 'error', message: e instanceof Error ? e.message : 'Something went wrong.' });
      });
    return () => ctl.abort();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key]);
  return state;
}

function Loading() {
  return (
    <div className="flex items-center gap-2 text-slate">
      <Spinner /> Loading
    </div>
  );
}

function ErrorBox({ message }: { message: string }) {
  return (
    <Card className="p-4 border border-danger/30 text-danger" >
      {message}
    </Card>
  );
}

export function RunStatusList() {
  const state = useLoad<RunSummary[]>((s) => listRunStatus(s), 'list');
  return (
    <div className="max-w-3xl mx-auto p-4">
      <h1 className="font-heading text-xl mb-1">Run status</h1>
      <p className="text-sm text-slate mb-4">Read-only view of sample runs. Nothing here changes a run.</p>
      {state.kind === 'loading' && <Loading />}
      {state.kind === 'error' && <ErrorBox message={state.message} />}
      {state.kind === 'ok' && state.data.length === 0 && <p className="text-slate">No runs to show.</p>}
      {state.kind === 'ok' && state.data.length > 0 && (
        <ul className="space-y-2">
          {state.data.map((r) => (
            <li key={r.run_id}>
              <Link to={`/runs/${r.run_id}`}>
                <Card className="p-3 flex items-center justify-between hover:border-teal">
                  <span>
                    <span className="font-medium">{r.deal_label}</span>{' '}
                    <span className="text-xs text-slate">{r.run_id}</span>
                  </span>
                  <StateBadge state={r.display_state} />
                </Card>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export function RunStatusDetail() {
  const { id = '' } = useParams();
  const state = useLoad<RunView>((s) => getRunStatus(id, s), id);
  return (
    <div className="max-w-3xl mx-auto p-4">
      <Link to="/runs" className="text-sm text-teal">
        All runs
      </Link>
      {state.kind === 'loading' && <Loading />}
      {state.kind === 'error' && <ErrorBox message={state.message} />}
      {state.kind === 'ok' && (
        <>
          <h1 className="font-heading text-xl my-2">{state.data.deal_label}</h1>
          <p className="text-xs text-slate mb-3">
            {state.data.run_id} / {state.data.status} / {state.data.phase}
          </p>
          <StateBanner run={state.data} />
          <GateList gates={state.data.gates} />
          <HeadlineList items={state.data.headline} diagnostic={state.data.values_are_diagnostic} />
          <EvidenceList items={state.data.evidence} />
          <HoldList holds={state.data.holds} />
          <EventTimeline events={state.data.events} />
        </>
      )}
    </div>
  );
}
