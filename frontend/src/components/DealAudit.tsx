import { useEffect, useState } from 'react';
import {
  History,
  Flag,
  Sparkles,
  Shield,
  Database,
  AlertTriangle,
  Loader2,
  type LucideIcon,
} from 'lucide-react';
import { getDealAudit, ApiError, type DealAuditResponse, type AuditEvent } from '../lib/api';
import { Card, Badge, statusTone } from './ui';
import { fmtDateTime, prettyStatus } from '../lib/format';

// ---------------------------------------------------------------------------
// DealAudit — the "Activity" tab on /deal/:id.
// GET /api/deals/{id}/audit: every job that ever ran for the deal (newest job
// first), each with its append-only AuditEvent list in insertion order.
// Rendered as one vertical timeline per job; event kind -> icon + color.
// ---------------------------------------------------------------------------

const KIND_STYLE: Record<string, { icon: LucideIcon; dot: string; label: string }> = {
  phase: { icon: Flag, dot: 'bg-slate/10 text-slate/60 border-slate/20', label: 'Phase' },
  llm_call: { icon: Sparkles, dot: 'bg-teal-panel text-teal border-teal/30', label: 'LLM call' },
  gate: { icon: Shield, dot: 'bg-warn/10 text-warn border-warn/30', label: 'Gate' },
  spec_mutation: {
    icon: Database,
    dot: 'bg-slate/10 text-slate border-slate/30',
    label: 'Spec write',
  },
  error: { icon: AlertTriangle, dot: 'bg-danger/10 text-danger border-danger/30', label: 'Error' },
};

const FALLBACK_STYLE = KIND_STYLE.phase;

function detailText(detail: unknown): string {
  if (typeof detail === 'string') return detail;
  try {
    return JSON.stringify(detail, null, 2);
  } catch {
    return String(detail);
  }
}

function TimelineEvent({ ev, isLast }: { ev: AuditEvent; isLast: boolean }) {
  const style = KIND_STYLE[ev.kind] ?? FALLBACK_STYLE;
  const Icon = style.icon;
  return (
    <li className="relative pl-10 pb-5 last:pb-1">
      {/* connector line down to the next event's dot */}
      {!isLast && <span className="absolute left-[13px] top-8 bottom-0 w-px bg-slate/15" aria-hidden />}
      <span
        className={`absolute left-0 top-0 w-7 h-7 rounded-full border flex items-center justify-center ${style.dot}`}
      >
        <Icon className="w-3.5 h-3.5" />
      </span>
      <div className="flex flex-wrap items-baseline gap-x-2 gap-y-0.5">
        <span className="text-[10px] font-label font-semibold uppercase tracking-wide text-slate/40">
          {style.label}
        </span>
        <span className="text-[10px] text-slate/35 tnum">{fmtDateTime(ev.ts)}</span>
      </div>
      <p className={`text-sm mt-0.5 ${ev.kind === 'error' ? 'text-danger' : 'text-slate/80'}`}>
        {ev.message}
      </p>
      {ev.detail != null && (
        <details className="mt-1">
          <summary className="text-xs text-slate/45 cursor-pointer hover:text-teal select-none">
            detail
          </summary>
          <pre className="mt-1 font-mono text-xs bg-slate/5 border border-slate/10 rounded-lg p-3 overflow-x-auto whitespace-pre-wrap">
            {detailText(ev.detail)}
          </pre>
        </details>
      )}
    </li>
  );
}

export function DealAudit({ dealId }: { dealId: string }) {
  const [data, setData] = useState<DealAuditResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    getDealAudit(dealId)
      .then((res) => {
        if (cancelled) return;
        setData(res);
        setLoading(false);
      })
      .catch((e) => {
        if (cancelled) return;
        if (e instanceof ApiError && e.status === 401) return; // global handler bounced
        setError(e instanceof Error ? e.message : String(e));
        setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [dealId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-16 text-slate/50">
        <Loader2 className="w-5 h-5 animate-spin mr-2" /> Loading activity…
      </div>
    );
  }

  if (error) {
    return (
      <Card className="p-4 border-danger/30 bg-danger/5">
        <div className="flex items-center gap-2 text-danger text-sm">
          <AlertTriangle className="w-4 h-4" /> {error}
        </div>
      </Card>
    );
  }

  const jobs = data?.jobs ?? [];

  return (
    <div className="space-y-4">
      <h2 className="eyebrow text-slate/60 flex items-center">
        <History className="w-4 h-4 mr-2" /> Activity
        <span className="ml-2 normal-case font-normal text-xs text-slate/50">
          — every run&rsquo;s append-only audit trail, newest first
        </span>
      </h2>

      {jobs.length === 0 ? (
        <Card className="p-8 text-center">
          <p className="text-sm text-slate/60">
            No activity recorded for this deal yet — underwrite runs append their audit trail
            here as they execute.
          </p>
        </Card>
      ) : (
        jobs.map((job) => (
          <Card key={job.job_id} className="p-5">
            <div className="flex flex-wrap items-center gap-2 mb-4 pb-3 border-b border-slate/10">
              <span className="text-xs font-mono text-slate/50 truncate max-w-[240px]" title={job.job_id}>
                {job.job_id}
              </span>
              <Badge tone={statusTone(job.status)}>{prettyStatus(job.status)}</Badge>
              <span className="text-xs text-slate/40 ml-auto tnum">
                started {fmtDateTime(job.created_at)}
              </span>
            </div>
            {job.events.length === 0 ? (
              <p className="text-xs text-slate/40">No events recorded on this job.</p>
            ) : (
              <ol>
                {job.events.map((ev, idx) => (
                  <TimelineEvent key={idx} ev={ev} isLast={idx === job.events.length - 1} />
                ))}
              </ol>
            )}
          </Card>
        ))
      )}
    </div>
  );
}
