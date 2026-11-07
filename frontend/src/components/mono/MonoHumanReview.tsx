import { useState } from 'react';
import { Badge, Button, Card, Spinner } from '../ui';
import { monoConflict, monoError, recordMonoGate, revisionOf, type MonoGateRequest, type MonoView } from '../../lib/monoApi';
import { asRecord, Details, Evidence } from './MonoEvidence';

export function MonoHumanReview({ view, onSaved, onReread }: { view: MonoView; onSaved: (view: MonoView) => void; onReread: () => Promise<void> }) {
  const [compsReason, setCompsReason] = useState('');
  const [decisionReason, setDecisionReason] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [conflicted, setConflicted] = useState(false);
  const [draftRevision, setDraftRevision] = useState(view.revision);
  const [retryRequest, setRetryRequest] = useState<{ fingerprint: string; key: string } | null>(null);
  const compsDigest = view.identity.source_hashes.comps;
  const compsConfirmed = view.gates.comps?.decision === 'confirm';
  const checksPassed = asRecord(view.current_result?.checks).release_passed === true;
  const canGo = view.can_edit && view.readiness.ready && Boolean(view.current_result) && checksPassed && compsConfirmed && Boolean(compsDigest);
  const revisionChanged = draftRevision !== view.revision;

  const submit = async (gate: MonoGateRequest['gate'], decision: MonoGateRequest['decision']) => {
    const reason = gate === 'comps' ? compsReason : decisionReason;
    if (!reason.trim() || revisionChanged || conflicted) return;
    const body: Omit<MonoGateRequest, 'idempotency_key'> = { ...revisionOf(view), gate, decision, reason };
    if (gate === 'comps') body.comps_sha256 = compsDigest;
    if (decision === 'go') body.result_id = view.current_result?.result_id;
    const fingerprint = JSON.stringify(body);
    const key = retryRequest?.fingerprint === fingerprint ? retryRequest.key : crypto.randomUUID();
    setRetryRequest({ fingerprint, key }); setBusy(true); setError(null);
    try {
      const next = await recordMonoGate(view.deal_id, { ...body, idempotency_key: key });
      onSaved(next);
      if (gate === 'comps') setCompsReason(''); else setDecisionReason('');
      setDraftRevision(next.revision);
    } catch (failure) {
      const conflict = monoConflict(failure);
      setConflicted(Boolean(conflict)); setError(conflict?.message ?? monoError(failure));
    } finally { setBusy(false); }
  };

  const reread = async () => {
    setBusy(true);
    try { await onReread(); setError('Latest revision loaded. Review the result and evidence before confirming a decision.'); }
    catch (failure) { setError(monoError(failure)); }
    finally { setBusy(false); }
  };

  return <section aria-label="Human review" className="space-y-4"><div><p className="eyebrow text-teal">Human checkpoint</p><h2 className="text-2xl mt-1">Review and decide</h2><p className="text-sm text-slate/60 mt-1">These are separate recorded human actions. Calculator completion does not approve a deal.</p></div>
    <Badge tone="warn">{view.gates.status}</Badge>
    {!view.can_edit && <p className="text-sm text-slate/60">Your current access allows viewing only. An authorized authenticated person must record decisions.</p>}
    {(revisionChanged || conflicted) && <div className="p-4 rounded-lg border border-warn/30 bg-warn/5 space-y-3"><p className="text-sm">The reviewed revision needs attention. Your reasons are preserved. Review revision {view.revision} and its current evidence before resubmitting.</p><div className="flex gap-2 flex-wrap"><Button variant="secondary" disabled={busy} onClick={() => { void reread(); }}>Reread latest revision</Button><Button variant="secondary" disabled={busy} onClick={() => { setDraftRevision(view.revision); setConflicted(false); setError(null); setRetryRequest(null); }}>I reviewed revision {view.revision}</Button></div></div>}
    {error && <p role="alert" className="text-sm text-danger">{error}</p>}
    <div className="grid lg:grid-cols-2 gap-4">
      <Card className="p-5 space-y-4"><div className="flex justify-between gap-2"><h3 className="text-xl">1. Confirm comps</h3><Badge tone={compsConfirmed ? 'ok' : 'warn'}>{compsConfirmed ? 'Confirmed' : 'Needs review'}</Badge></div>
        <p className="text-sm text-slate/70">Confirm the comparable evidence for revision {view.revision}. The recorded identity includes the comps digest.</p>
        <p className="text-xs break-all text-slate/60">Comps SHA-256: {compsDigest || 'Missing verified comps identity'}</p>
        <label className="block text-sm">Comps review reason<textarea className="input mt-1" rows={3} value={compsReason} disabled={!view.can_edit || busy} onChange={(event) => setCompsReason(event.target.value)} /></label>
        <Button disabled={!view.can_edit || busy || !compsReason.trim() || !compsDigest || revisionChanged || conflicted} onClick={() => { void submit('comps', 'confirm'); }}>{busy && <Spinner />}Confirm comps</Button>
        <Details title="Recorded comps decision and actor"><Evidence value={view.gates.comps} /></Details>
      </Card>
      <Card className="p-5 space-y-4"><div className="flex justify-between gap-2"><h3 className="text-xl">2. Go or no-go</h3><Badge tone="neutral">{String(view.gates.go_no_go?.decision ?? 'Awaiting decision')}</Badge></div>
        <p className="text-sm text-slate/70">A go decision requires readiness, verified release checks, the exact current result and confirmed comps. A no-go can record a reason while evidence remains incomplete.</p>
        <ul className="text-xs space-y-1 text-slate/70"><li>Readiness: {view.readiness.ready ? 'Ready' : 'Incomplete'}</li><li>Current result: {view.current_result ? view.current_result.result_id : 'Missing'}</li><li>Release checks: {checksPassed ? 'Verified passing' : 'Not verified passing'}</li><li>Comps: {compsConfirmed ? 'Confirmed on this revision' : 'Not confirmed'}</li></ul>
        <label className="block text-sm">Decision reason<textarea className="input mt-1" rows={3} value={decisionReason} disabled={!view.can_edit || busy} onChange={(event) => setDecisionReason(event.target.value)} /></label>
        <div className="flex gap-2 flex-wrap"><Button disabled={!canGo || busy || !decisionReason.trim() || revisionChanged || conflicted} onClick={() => { void submit('go_no_go', 'go'); }}>Record go</Button><Button variant="secondary" disabled={!view.can_edit || busy || !decisionReason.trim() || revisionChanged || conflicted} onClick={() => { void submit('go_no_go', 'no_go'); }}>Record no-go</Button></div>
        <Details title="Recorded go/no-go decision and actor"><Evidence value={view.gates.go_no_go} /></Details>
      </Card>
    </div>
  </section>;
}

export function MonoNarrative({ view }: { view: MonoView }) {
  const narrative = view.narrative;
  const stale = narrative.revision !== view.revision;
  const disabled = narrative.status === 'disabled';
  return <Card className="p-5 space-y-3"><div className="flex flex-wrap gap-2 items-center justify-between"><h2 className="text-2xl">Argue against this deal</h2><Badge tone={stale ? 'warn' : 'neutral'}>{stale ? 'Stale narrative' : narrative.status}</Badge></div>
    <p className="text-xs text-slate/60">Provider: {narrative.provider} · Narrative revision {narrative.revision} · Current revision {view.revision}</p>
    {disabled && <p className="text-sm text-slate/70">The judgment provider is disabled. No live judgment run has been verified.</p>}
    {narrative.provider === 'fixture' && <p className="text-sm text-warn">Engineering fixture content exercises this panel. It is not verified judgment.</p>}
    {stale && <p className="text-sm text-warn">Inputs changed after this narrative. Review the current evidence before relying on it.</p>}
    <p className="whitespace-pre-wrap text-sm text-slate/80">{narrative.text || 'No narrative recorded.'}</p>
    <Details title="Supporting references and uncertainty"><Evidence value={narrative.references} /><Evidence value={Object.fromEntries(Object.entries(narrative).filter(([key]) => !['status', 'provider', 'revision', 'text', 'references'].includes(key)))} label="Narrative details" /></Details>
    <p className="text-xs text-slate/60">Narrative is read only. It cannot change assumptions, outputs or human decisions.</p>
  </Card>;
}
