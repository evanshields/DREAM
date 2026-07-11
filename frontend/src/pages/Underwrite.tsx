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
  Building2,
  Landmark,
  CheckCircle2,
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

// EFB intake fields (percent fields entered as percent, e.g. 5 => 0.05 —
// same convention as BondScreen). Defaults mirror the backend request model.
interface EFBFields {
  stabilizedNoi: string;
  targetDscr: string;
  bondRate: string; // percent
  amortYears: string;
  taxExempted: string; // optional
  holdYears: string;
}

const EFB_FIELD_DEFAULTS: EFBFields = {
  stabilizedNoi: '',
  targetDscr: '1.15',
  bondRate: '5',
  amortYears: '35',
  taxExempted: '',
  holdYears: '10',
};

// blocking-question fields answered as a percent in the UI, sent as a decimal
const isPctField = (field: string): boolean =>
  field.endsWith('exit_cap') || field.endsWith('bond_rate');

export function Underwrite() {
  const navigate = useNavigate();

  // intake form
  const [dealName, setDealName] = useState('');
  const [routing, setRouting] = useState<'ACQ' | 'EFB'>('ACQ');
  const [purchasePrice, setPurchasePrice] = useState('');
  const [holdYears, setHoldYears] = useState('');
  const [exitCap, setExitCap] = useState(''); // entered as percent (6.0 => 0.06)
  const [efb, setEfb] = useState<EFBFields>(EFB_FIELD_DEFAULTS);
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
    if (routing === 'EFB') {
      // percent entered as percent (5 => 0.05); leave a field blank and the
      // analysts ask for it (stabilized NOI is required by the form).
      if (efb.stabilizedNoi.trim() !== '') critical_inputs.stabilized_noi = Number(efb.stabilizedNoi);
      if (efb.targetDscr.trim() !== '') critical_inputs.target_dscr = Number(efb.targetDscr);
      if (efb.bondRate.trim() !== '') critical_inputs.bond_rate = Number(efb.bondRate) / 100;
      if (efb.amortYears.trim() !== '') critical_inputs.amortization_years = Number(efb.amortYears);
      if (efb.taxExempted.trim() !== '')
        critical_inputs.annual_property_tax_exempted = Number(efb.taxExempted);
      if (efb.holdYears.trim() !== '') critical_inputs.hold_years = Number(efb.holdYears);
    } else {
      if (purchasePrice.trim() !== '') critical_inputs.purchase_price = Number(purchasePrice);
      if (holdYears.trim() !== '') critical_inputs.hold_years = Number(holdYears);
      if (exitCap.trim() !== '') critical_inputs.exit_cap = Number(exitCap) / 100;
    }

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
            efb,
            setEfb,
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
  efb: EFBFields;
  setEfb: React.Dispatch<React.SetStateAction<EFBFields>>;
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

          <div className="sm:col-span-2">
            <span className="label">Routing</span>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3" role="radiogroup" aria-label="Routing">
              <RoutingCard
                active={p.routing === 'ACQ'}
                onSelect={() => p.setRouting('ACQ')}
                icon={Building2}
                title="Market-Rate Acquisition"
                sub="Value-add bridge-to-agency · IRR / equity multiple / CoC"
              />
              <RoutingCard
                active={p.routing === 'EFB'}
                onSelect={() => p.setRouting('EFB')}
                icon={Landmark}
                title="Tax-Exempt Bond (EFB)"
                sub="501(c)(3) essential-function bond sized to a target DSCR"
              />
            </div>
          </div>

          {p.routing === 'ACQ' ? (
            <>
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
            </>
          ) : (
            <EFBCriticalInputs efb={p.efb} setEfb={p.setEfb} />
          )}
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

// --- routing selector card ---------------------------------------------------
function RoutingCard({
  active,
  onSelect,
  icon: Icon,
  title,
  sub,
}: {
  active: boolean;
  onSelect: () => void;
  icon: typeof Building2;
  title: string;
  sub: string;
}) {
  return (
    <button
      type="button"
      role="radio"
      aria-checked={active ? 'true' : 'false'}
      onClick={onSelect}
      className={[
        'relative text-left rounded-xl border p-4 transition-colors',
        active
          ? 'border-teal bg-teal-panel/60 shadow-card'
          : 'border-slate/15 bg-white hover:border-teal/40',
      ].join(' ')}
    >
      {active && <CheckCircle2 className="absolute top-3 right-3 w-4 h-4 text-teal" />}
      <span
        className={`flex items-center gap-2 font-label font-semibold text-sm ${
          active ? 'text-teal' : 'text-slate'
        }`}
      >
        <Icon className="w-4 h-4" /> {title}
      </span>
      <span className="block text-xs text-slate/60 mt-1 leading-snug">{sub}</span>
    </button>
  );
}

// --- EFB critical inputs (percent entered as percent, same as BondScreen) -----
function EFBCriticalInputs({
  efb,
  setEfb,
}: {
  efb: EFBFields;
  setEfb: React.Dispatch<React.SetStateAction<EFBFields>>;
}) {
  const set = (patch: Partial<EFBFields>) => setEfb((prev) => ({ ...prev, ...patch }));

  return (
    <>
      <div>
        <label htmlFor="efbNoi" className="label">
          Stabilized NOI ($) <span className="text-danger">*</span>
        </label>
        <Input
          id="efbNoi"
          type="number"
          step="10000"
          value={efb.stabilizedNoi}
          onChange={(e) => set({ stabilizedNoi: e.target.value })}
          placeholder="2500000"
          required
        />
      </div>

      <div>
        <label htmlFor="efbDscr" className="label">
          Target DSCR (x)
        </label>
        <Input
          id="efbDscr"
          type="number"
          step="0.01"
          value={efb.targetDscr}
          onChange={(e) => set({ targetDscr: e.target.value })}
          placeholder="1.15"
        />
        <p className="text-xs text-slate/40 mt-1">1.15x with HAP · 1.20x without</p>
      </div>

      <div>
        <label htmlFor="efbRate" className="label">
          Bond rate (%)
        </label>
        <Input
          id="efbRate"
          type="number"
          step="0.05"
          value={efb.bondRate}
          onChange={(e) => set({ bondRate: e.target.value })}
          placeholder="5.0"
        />
      </div>

      <div>
        <label htmlFor="efbAmort" className="label">
          Amortization (years)
        </label>
        <Input
          id="efbAmort"
          type="number"
          step="1"
          value={efb.amortYears}
          onChange={(e) => set({ amortYears: e.target.value })}
          placeholder="35"
        />
      </div>

      <div>
        <label htmlFor="efbTax" className="label">
          Annual property tax exempted ($)
        </label>
        <Input
          id="efbTax"
          type="number"
          step="10000"
          value={efb.taxExempted}
          onChange={(e) => set({ taxExempted: e.target.value })}
          placeholder="optional"
        />
        <p className="text-xs text-slate/40 mt-1">Optional · drives the tax-savings metric only</p>
      </div>

      <div>
        <label htmlFor="efbHold" className="label">
          Hold (years)
        </label>
        <Input
          id="efbHold"
          type="number"
          step="1"
          value={efb.holdYears}
          onChange={(e) => set({ holdYears: e.target.value })}
          placeholder="10"
        />
      </div>
    </>
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
    // exit_cap / bond_rate entered as percent; numeric fields as numbers; routing/string as-is.
    if (isPctField(q.field)) return Number(raw) / 100;
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
              {isPctField(q.field) && (
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
