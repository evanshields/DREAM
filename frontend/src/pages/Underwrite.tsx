import { useState, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Rocket,
  Loader2,
  AlertTriangle,
  HelpCircle,
  Ban,
  ArrowRight,
  FileText,
} from 'lucide-react';
import {
  submitJob,
  answerJob,
  cancelJob,
  ApiError,
  type JobView,
  type OpenQuestion,
} from '../lib/api';
import { Card, Button, Input, Badge } from '../components/ui';

// Phase text shown while the synchronous submit runs (20s–4min with live Kimi).
const RUNNING_STATUSES = new Set(['submitted', 'routing', 'analyzing', 'synthesizing']);

type Stage = 'intake' | 'running' | 'questions' | 'failed';

export function Underwrite() {
  const navigate = useNavigate();

  // intake form
  const [dealName, setDealName] = useState('');
  const [routing, setRouting] = useState<'ACQ' | 'EFB'>('ACQ');
  const [purchasePrice, setPurchasePrice] = useState('');
  const [holdYears, setHoldYears] = useState('');
  const [exitCap, setExitCap] = useState(''); // entered as percent (6.0 => 0.06)
  const [notes, setNotes] = useState('');

  const [stage, setStage] = useState<Stage>('intake');
  const [job, setJob] = useState<JobView | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const abortRef = useRef<AbortController | null>(null);

  // route a returned job view to the right stage / navigation.
  const applyJob = useCallback(
    (view: JobView) => {
      setJob(view);
      if (view.status === 'awaiting_cp1' || view.status === 'completed') {
        // CP-1 review lives on the deal detail screen — carry the full job view so it can render
        // gates + open questions + headline immediately (no single-deal GET endpoint by contract).
        navigate(`/deal/${encodeURIComponent(view.deal_id)}`, { replace: true, state: { job: view } });
        return;
      }
      if (view.status === 'failed') {
        setStage('failed');
        return;
      }
      if (view.status === 'awaiting_input') {
        setStage('questions');
        return;
      }
      if (RUNNING_STATUSES.has(view.status)) {
        setStage('running');
        return;
      }
      // cancelled or anything else → back to intake with a note.
      setStage('intake');
    },
    [navigate],
  );

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setBusy(true);
    setStage('running');

    const critical_inputs: Record<string, unknown> = {};
    if (purchasePrice.trim() !== '') critical_inputs.purchase_price = Number(purchasePrice);
    if (holdYears.trim() !== '') critical_inputs.hold_years = Number(holdYears);
    if (exitCap.trim() !== '') critical_inputs.exit_cap = Number(exitCap) / 100;

    const name = dealName.trim() || 'Untitled deal';
    const ctrl = new AbortController();
    abortRef.current = ctrl;

    try {
      const view = await submitJob(
        {
          intake_summary: { routing, deal_name: name, critical_inputs },
          deal_docs: notes.trim() ? { notes: notes.trim() } : {},
          owner: '',
          deal_name: name,
          routing,
        },
        ctrl.signal,
      );
      applyJob(view);
    } catch (err) {
      if (ctrl.signal.aborted) {
        setStage('intake');
        return;
      }
      if (err instanceof ApiError && err.status === 401) return; // global handler
      setError(err instanceof Error ? err.message : String(err));
      setStage('intake');
    } finally {
      setBusy(false);
    }
  };

  const handleCancel = async () => {
    abortRef.current?.abort();
    if (job?.job_id) {
      try {
        await cancelJob(job.job_id);
      } catch {
        /* best-effort */
      }
    }
    setStage('intake');
    setBusy(false);
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-head font-bold text-slate-near">New Underwrite</h1>
        <p className="text-sm text-slate/60 mt-1">
          The analysts run an autonomous first pass to a CP-1 review. Missing inputs come back as
          questions — answer them and the run resumes.
        </p>
      </div>

      {error && (
        <Card className="p-4 border-danger/30 bg-danger/5">
          <div className="flex items-center gap-2 text-danger text-sm">
            <AlertTriangle className="w-4 h-4 shrink-0" /> {error}
          </div>
        </Card>
      )}

      {stage === 'intake' && (
        <IntakeForm
          {...{
            dealName,
            setDealName,
            routing,
            setRouting,
            purchasePrice,
            setPurchasePrice,
            holdYears,
            setHoldYears,
            exitCap,
            setExitCap,
            notes,
            setNotes,
            busy,
            onSubmit: handleSubmit,
          }}
        />
      )}

      {stage === 'running' && <RunningPanel onCancel={handleCancel} />}

      {stage === 'questions' && job && (
        <QuestionsPanel job={job} onResolved={applyJob} onError={setError} onCancel={handleCancel} />
      )}

      {stage === 'failed' && job && (
        <FailedPanel job={job} onRetry={() => setStage('intake')} />
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Intake form
// ---------------------------------------------------------------------------
interface IntakeProps {
  dealName: string;
  setDealName: (v: string) => void;
  routing: 'ACQ' | 'EFB';
  setRouting: (v: 'ACQ' | 'EFB') => void;
  purchasePrice: string;
  setPurchasePrice: (v: string) => void;
  holdYears: string;
  setHoldYears: (v: string) => void;
  exitCap: string;
  setExitCap: (v: string) => void;
  notes: string;
  setNotes: (v: string) => void;
  busy: boolean;
  onSubmit: (e: React.FormEvent) => void;
}

function IntakeForm(p: IntakeProps) {
  return (
    <Card className="p-6">
      <form onSubmit={p.onSubmit} className="space-y-5">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
          <div className="sm:col-span-2">
            <label htmlFor="dealName" className="label">
              Deal name
            </label>
            <Input
              id="dealName"
              value={p.dealName}
              onChange={(e) => p.setDealName(e.target.value)}
              placeholder="Esplanade Apartments"
              autoFocus
            />
          </div>

          <div>
            <label htmlFor="routing" className="label">
              Routing
            </label>
            <select
              id="routing"
              value={p.routing}
              onChange={(e) => p.setRouting(e.target.value as 'ACQ' | 'EFB')}
              className="input"
            >
              <option value="ACQ">ACQ — Acquisition (value-add)</option>
              <option value="EFB">EFB — Essential Function Bond</option>
            </select>
          </div>

          <div>
            <label htmlFor="purchasePrice" className="label">
              Purchase price ($)
            </label>
            <Input
              id="purchasePrice"
              type="number"
              step="100000"
              value={p.purchasePrice}
              onChange={(e) => p.setPurchasePrice(e.target.value)}
              placeholder="55000000"
            />
          </div>

          <div>
            <label htmlFor="holdYears" className="label">
              Hold (years)
            </label>
            <Input
              id="holdYears"
              type="number"
              step="1"
              value={p.holdYears}
              onChange={(e) => p.setHoldYears(e.target.value)}
              placeholder="7"
            />
          </div>

          <div>
            <label htmlFor="exitCap" className="label">
              Exit cap (%)
            </label>
            <Input
              id="exitCap"
              type="number"
              step="0.05"
              value={p.exitCap}
              onChange={(e) => p.setExitCap(e.target.value)}
              placeholder="6.0"
            />
          </div>
        </div>

        <div>
          <label htmlFor="notes" className="label flex items-center gap-1.5">
            <FileText className="w-3.5 h-3.5" /> Deal notes / paste (optional)
          </label>
          <textarea
            id="notes"
            value={p.notes}
            onChange={(e) => p.setNotes(e.target.value)}
            rows={5}
            className="input resize-y font-mono text-xs"
            placeholder="Paste broker OM excerpts, rent roll, T-12 notes — the analysts read this."
          />
        </div>

        <div className="flex items-center justify-between pt-2">
          <p className="text-xs text-slate/50">
            Leave a critical input blank and the analysts will ask for it.
          </p>
          <Button type="submit" icon={p.busy ? undefined : Rocket} disabled={p.busy}>
            {p.busy ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" /> Submitting…
              </>
            ) : (
              'Run Underwrite'
            )}
          </Button>
        </div>
      </form>
    </Card>
  );
}

// ---------------------------------------------------------------------------
// Running (synchronous long call) panel
// ---------------------------------------------------------------------------
function RunningPanel({ onCancel }: { onCancel: () => void }) {
  return (
    <Card className="p-10 flex flex-col items-center text-center">
      <div className="w-16 h-16 rounded-full bg-teal-panel flex items-center justify-center mb-5">
        <Loader2 className="w-8 h-8 text-teal animate-spin" />
      </div>
      <h3 className="font-head font-bold text-xl text-slate-near mb-2">Underwriting…</h3>
      <p className="text-sm text-slate/60 max-w-md mb-1">
        The analysts are reading the deal, routing it, and running the validated engine. This can
        take a few minutes with a full deal package — please keep this tab open.
      </p>
      <p className="text-xs text-slate/40 mb-6">No LLM is used for any number once at CP-1.</p>
      <Button variant="secondary" icon={Ban} onClick={onCancel}>
        Cancel
      </Button>
    </Card>
  );
}

// ---------------------------------------------------------------------------
// Blocking-questions panel (awaiting_input loop)
// ---------------------------------------------------------------------------
function QuestionsPanel({
  job,
  onResolved,
  onError,
  onCancel,
}: {
  job: JobView;
  onResolved: (v: JobView) => void;
  onError: (msg: string) => void;
  onCancel: () => void;
}) {
  const blocking = job.blocking_questions ?? [];
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [submitting, setSubmitting] = useState(false);

  const setAnswer = (id: string, value: string) =>
    setAnswers((a) => ({ ...a, [id]: value }));

  const coerce = (q: OpenQuestion, raw: string): unknown => {
    // exit_cap entered as percent; numeric fields as numbers; routing/string as-is.
    if (q.field.endsWith('exit_cap')) return Number(raw) / 100;
    const n = Number(raw);
    if (!q.options && raw.trim() !== '' && Number.isFinite(n)) return n;
    return raw;
  };

  const handleSubmitAll = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    onError('');
    let last: JobView = job;
    try {
      // Answer each blocking question in turn; the LAST answer resumes the run.
      for (const q of blocking) {
        const raw = answers[q.id] ?? '';
        last = await answerJob(job.job_id, q.id, coerce(q, raw));
      }
      onResolved(last);
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) return;
      onError(err instanceof Error ? err.message : String(err));
      setSubmitting(false);
    }
  };

  const allAnswered = blocking.every((q) => (answers[q.id] ?? '').trim() !== '');

  return (
    <Card className="p-6">
      <div className="flex items-center gap-2 mb-1">
        <HelpCircle className="w-5 h-5 text-warn" />
        <h3 className="font-head font-bold text-xl text-slate-near">A few inputs needed</h3>
        <Badge tone="warn">Awaiting input</Badge>
      </div>
      <p className="text-sm text-slate/60 mb-6">
        The analysts need these to complete the underwrite. Answer all, then resume.
      </p>

      <form onSubmit={handleSubmitAll} className="space-y-5">
        {blocking.map((q) => (
          <div key={q.id}>
            <label htmlFor={q.id} className="label">
              {q.question}
              {q.field.endsWith('exit_cap') && (
                <span className="ml-1 normal-case text-slate/40">(as %, e.g. 6.0)</span>
              )}
            </label>
            {q.options && q.options.length > 0 ? (
              <select
                id={q.id}
                className="input"
                value={answers[q.id] ?? ''}
                onChange={(e) => setAnswer(q.id, e.target.value)}
                required
              >
                <option value="" disabled>
                  Select…
                </option>
                {q.options.map((opt) => (
                  <option key={opt} value={opt}>
                    {opt}
                  </option>
                ))}
              </select>
            ) : (
              <Input
                id={q.id}
                value={answers[q.id] ?? ''}
                onChange={(e) => setAnswer(q.id, e.target.value)}
                placeholder="Your answer"
                required
              />
            )}
            <p className="text-xs text-slate/40 mt-1 font-mono">{q.field}</p>
          </div>
        ))}

        <div className="flex items-center justify-between pt-2">
          <Button type="button" variant="ghost" icon={Ban} onClick={onCancel}>
            Cancel
          </Button>
          <Button
            type="submit"
            icon={submitting ? undefined : ArrowRight}
            disabled={!allAnswered || submitting}
          >
            {submitting ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" /> Resuming…
              </>
            ) : (
              'Submit & Resume'
            )}
          </Button>
        </div>
      </form>
    </Card>
  );
}

// ---------------------------------------------------------------------------
// Failed panel
// ---------------------------------------------------------------------------
function FailedPanel({ job, onRetry }: { job: JobView; onRetry: () => void }) {
  return (
    <Card className="p-8 border-danger/30">
      <div className="flex items-center gap-2 mb-3">
        <AlertTriangle className="w-5 h-5 text-danger" />
        <h3 className="font-head font-bold text-xl text-slate-near">Underwrite failed</h3>
        <Badge tone="danger">Failed</Badge>
      </div>
      <p className="text-sm text-slate/70 mb-2">
        The run stopped before reaching CP-1. The reported reason:
      </p>
      <pre className="text-xs font-mono bg-danger/5 border border-danger/20 rounded-lg p-3 whitespace-pre-wrap text-danger mb-5">
        {job.error || 'No error detail provided.'}
      </pre>
      <Button variant="secondary" onClick={onRetry}>
        Back to intake
      </Button>
    </Card>
  );
}
