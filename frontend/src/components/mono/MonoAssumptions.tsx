import { useMemo, useState } from 'react';
import { Badge, Button, Input, Spinner } from '../ui';
import { editMonoAssumption, monoConflict, monoError, revisionOf, type MonoAssumption, type MonoScalar, type MonoView } from '../../lib/monoApi';
import { asRecord, Details, Evidence, monoText, monoValue, ProblemList } from './MonoEvidence';

type ValueKind = 'text' | 'number' | 'boolean' | 'null';

function AssumptionRow({ field, view, onSaved, onReread }: { field: MonoAssumption; view: MonoView; onSaved: (view: MonoView) => void; onReread: () => Promise<void> }) {
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState('');
  const [kind, setKind] = useState<ValueKind>('text');
  const [reason, setReason] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [conflict, setConflict] = useState(false);
  const [reviewedRevision, setReviewedRevision] = useState(view.revision);
  const [requestKey, setRequestKey] = useState<string | null>(null);
  const [requestFingerprint, setRequestFingerprint] = useState<string | null>(null);

  const start = () => {
    setDraft(field.value === null || field.value === undefined ? '' : String(field.value));
    setKind(field.value === null ? 'null' : typeof field.value === 'number' ? 'number' : typeof field.value === 'boolean' ? 'boolean' : 'text');
    setReason(''); setError(null); setConflict(false); setReviewedRevision(view.revision); setEditing(true);
    setRequestKey(null); setRequestFingerprint(null);
  };

  const save = async () => {
    setError(null);
    if (!reason.trim()) { setError('Explain why this assumption should change.'); return; }
    if (reviewedRevision !== view.revision) { setConflict(true); setError('Review the refreshed value and acknowledge this revision before saving.'); return; }
    let enteredValue: MonoScalar = draft;
    if (kind === 'null') enteredValue = null;
    if (kind === 'boolean') enteredValue = draft === 'true';
    // Preserve number entry as typed text. Python validates and normalizes it.
    // Never use Number(), percent multiplication or currency conversions here.
    const body = { ...revisionOf(view), field_id: field.id, entered_value: enteredValue, unit: field.unit, reason };
    const fingerprint = JSON.stringify(body);
    const key = fingerprint === requestFingerprint && requestKey ? requestKey : crypto.randomUUID();
    setRequestKey(key); setRequestFingerprint(fingerprint); setBusy(true);
    try {
      const next = await editMonoAssumption(view.deal_id, { ...body, idempotency_key: key });
      onSaved(next);
      if (next.operation && next.operation.applied_revision < next.revision) {
        setConflict(true);
        setError(`Your save was recorded in revision ${next.operation.applied_revision}. A newer revision exists. Review it before changing again.`);
      } else { setEditing(false); setConflict(false); }
    } catch (failure) {
      const changed = monoConflict(failure);
      setConflict(Boolean(changed));
      setError(changed?.message ?? monoError(failure));
      if (changed) {
        // Read the newer revision while preserving this row's unsaved entry.
        try { await onReread(); } catch { /* Keep the conflict and block resubmission. */ }
      }
    } finally { setBusy(false); }
  };

  const reread = async () => {
    setBusy(true);
    try { await onReread(); setError('Latest revision loaded. Your entry is preserved. Review it before resubmitting.'); }
    catch (failure) { setError(monoError(failure)); }
    finally { setBusy(false); }
  };

  const changedUnderDraft = editing && reviewedRevision !== view.revision;
  return <article className="border-t border-slate/10 p-4 sm:p-5 space-y-3" data-field-id={field.id}>
    <div className="flex flex-wrap gap-4 items-start justify-between">
      <div className="min-w-0 flex-1">
        <div className="flex flex-wrap gap-2 items-center"><h4 className="font-semibold text-sm">{field.label || field.id}</h4><Badge tone={field.bucket === 'D' ? 'warn' : 'neutral'}>Bucket {field.bucket || 'Unknown'}</Badge></div>
        <p className="text-xs text-slate/50 mt-1 break-all">{field.id}</p>
        <div className="mt-3 text-xl tnum font-semibold whitespace-pre-wrap break-words">{monoValue(field.value, field.unit)} <span className="text-xs font-normal text-slate/60">{field.unit === '%' ? 'Percent' : field.unit || 'Unit not recorded'}</span></div>
        {Object.prototype.hasOwnProperty.call(field.source ?? {}, 'initially_recorded_value') && <p className="text-xs text-slate/60 mt-1">Initially recorded: {monoValue(asRecord(field.source).initially_recorded_value, field.unit)}</p>}
      </div>
      {view.can_edit && !editing && <Button variant="secondary" onClick={start} aria-label={`Edit ${field.label || field.id}`}>Edit</Button>}
    </div>
    <div className="text-xs flex flex-wrap gap-x-5 gap-y-2 text-slate/70">
      <span>Recorded applicability: <strong>{monoText(field.applicability)}</strong></span>
      <span>Verified applicability: <strong>{field.verified_applicability?.status || 'Unknown'}</strong></span>
    </div>
    {field.verified_applicability?.reason && <p className="text-sm text-slate/70">{field.verified_applicability.reason}</p>}
    {field.verified_applicability?.rule_id && <p className="text-xs text-slate/60">Rule: {field.verified_applicability.rule_id}</p>}
    <ProblemList values={field.missing_reasons ?? []} empty="No missing-evidence reason recorded." />
    {editing && <div className="rounded-lg bg-teal-panel border border-teal/20 p-4 space-y-3">
      <p className="text-sm font-semibold">Edit assumption in {field.unit || 'the recorded unit'}</p>
      <div className="grid sm:grid-cols-[10rem_1fr] gap-3">
        <label className="text-sm">Value type<select className="input mt-1" value={kind} onChange={(event) => { const next = event.target.value as ValueKind; setKind(next); if (next === 'boolean' && draft !== 'true' && draft !== 'false') setDraft('false'); }}>
          <option value="text">Text</option><option value="number">Number entry</option><option value="boolean">True or false</option><option value="null">Null</option>
        </select></label>
        <label className="text-sm">Entered value{kind === 'boolean' ? <select className="input mt-1" value={draft} onChange={(event) => setDraft(event.target.value)}><option value="true">true</option><option value="false">false</option></select> : <Input className="mt-1" aria-label={`New value for ${field.label}`} disabled={kind === 'null'} value={kind === 'null' ? 'null' : draft} onChange={(event) => setDraft(event.target.value)} />}</label>
      </div>
      <p className="text-xs text-slate/60">An empty text value, null and zero have different meanings. The server validates your entry in the recorded unit.</p>
      <label className="block text-sm">Reason<textarea className="input mt-1" rows={2} value={reason} onChange={(event) => setReason(event.target.value)} /></label>
      {error && <p role="alert" className="text-sm text-danger">{error}</p>}
      {(conflict || changedUnderDraft) && <div className="space-y-2 border border-warn/30 rounded-lg p-3 text-sm"><p>Your entry is preserved. Current revision: {view.revision}. Current value: {monoText(field.value)}.</p><div className="flex flex-wrap gap-2"><Button variant="secondary" disabled={busy} onClick={() => { void reread(); }}>Reread latest revision</Button><Button variant="secondary" disabled={busy || !changedUnderDraft} onClick={() => { setReviewedRevision(view.revision); setConflict(false); setError(null); setRequestKey(null); setRequestFingerprint(null); }}>I reviewed revision {view.revision}</Button></div></div>}
      <div className="flex gap-2"><Button disabled={busy || changedUnderDraft || conflict || !view.can_edit || !reason.trim()} onClick={() => { void save(); }}>{busy && <Spinner />}Save assumption</Button><Button variant="ghost" disabled={busy} onClick={() => setEditing(false)}>Discard edit</Button></div>
    </div>}
    <div className="grid sm:grid-cols-2 gap-2">
      <Details title="Original source and applicability evidence"><Evidence value={field.source} label={`Source for ${field.id}`} /><Evidence value={field.verified_applicability?.evidence} label="Applicability evidence" /></Details>
      <Details title={`History (${field.history?.length ?? 0})`}><p className="text-xs text-slate/60">Original evidence and recorded decisions are retained.</p><Evidence value={field.history} label={`History for ${field.id}`} /></Details>
    </div>
  </article>;
}

export function MonoAssumptions({ view, onSaved, onReread }: { view: MonoView; onSaved: (view: MonoView) => void; onReread: () => Promise<void> }) {
  const [query, setQuery] = useState('');
  const [missingOnly, setMissingOnly] = useState(false);
  const groups = useMemo(() => {
    const result = new Map<string, MonoAssumption[]>();
    for (const field of view.assumptions) {
      const group = field.group || 'Other assumptions';
      const entries = result.get(group) ?? [];
      entries.push(field); result.set(group, entries);
    }
    return Array.from(result.entries());
  }, [view.assumptions]);
  const matches = (field: MonoAssumption) => (!missingOnly || field.missing_reasons.length > 0) && `${field.id} ${field.label} ${field.group}`.toLowerCase().includes(query.toLowerCase());
  const visibleCount = view.assumptions.filter(matches).length;
  return <section aria-label="Deal assumptions" className="space-y-4">
    <div className="flex flex-wrap items-end justify-between gap-3"><div><p className="eyebrow text-teal">Evidence and assumptions</p><h2 className="text-2xl mt-1">Every input, in context</h2><p className="text-sm text-slate/60 mt-1">{view.assumptions.length} assumptions across {groups.length} groups. {visibleCount} match the current filters.</p></div></div>
    <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center"><Input aria-label="Search assumptions" placeholder="Search by label, group or field ID" value={query} onChange={(event) => setQuery(event.target.value)} className="sm:max-w-md" /><label className="flex items-center gap-2 text-sm"><input type="checkbox" checked={missingOnly} onChange={(event) => setMissingOnly(event.target.checked)} />Show missing evidence only</label>{(query || missingOnly) && <Button variant="ghost" onClick={() => { setQuery(''); setMissingOnly(false); }}>Clear filters</Button>}</div>
    {visibleCount === 0 && <p className="p-5 border border-slate/10 rounded-lg text-sm">No assumptions match. Clear the filters to see every input.</p>}
    {groups.map(([group, fields], index) => <div key={group} hidden={!fields.some(matches)}><Details title={`${group} (${fields.filter(matches).length} of ${fields.length})`} open={(Boolean(query) || missingOnly) && fields.some(matches) || index < 2}>
      {fields.map((field) => <div key={field.id} hidden={!matches(field)}><AssumptionRow field={field} view={view} onSaved={onSaved} onReread={onReread} /></div>)}
    </Details></div>)}
  </section>;
}
