import { useEffect, useState } from 'react';
import {
  History,
  Flag,
  Sparkles,
  Shield,
  Database,
  AlertTriangle,
  StickyNote,
  CheckCircle2,
  Circle,
  Loader2,
  type LucideIcon,
} from 'lucide-react';
import {
  getDealTimeline,
  ApiError,
  type DealTimelineResponse,
  type TimelineEvent,
} from '../lib/api';
import { Card } from './ui';
import { fmtDateTime } from '../lib/format';

// ---------------------------------------------------------------------------
// DealTimeline — the "Activity" tab on /deal/:id (Phase 5). Consumes
// GET /api/deals/{id}/timeline: a READ-TIME merge of the append-only job audit
// with the deal's pinned notes + tasks, one newest-first feed grouped by month.
// Each event kind gets its own dot (icon + color); a vertical spine connects them.
// ---------------------------------------------------------------------------

interface RowStyle {
  icon: LucideIcon;
  dot: string;
  label: string;
}

// audit sub-kinds (phase|llm_call|gate|spec_mutation|error) + the two human sources (note|task).
const KIND_STYLE: Record<string, RowStyle> = {
  phase: { icon: Flag, dot: 'bg-slate/10 text-slate/60 border-slate/20', label: 'Phase' },
  llm_call: { icon: Sparkles, dot: 'bg-teal-panel text-teal border-teal/30', label: 'LLM call' },
  gate: { icon: Shield, dot: 'bg-warn/10 text-warn border-warn/30', label: 'Gate' },
  spec_mutation: { icon: Database, dot: 'bg-slate/10 text-slate border-slate/30', label: 'Spec write' },
  error: { icon: AlertTriangle, dot: 'bg-danger/10 text-danger border-danger/30', label: 'Error' },
  note: { icon: StickyNote, dot: 'bg-electric/10 text-electric border-electric/30', label: 'Note' },
  task: { icon: Circle, dot: 'bg-taupe/30 text-slate border-taupe', label: 'Task' },
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

function EventRow({ ev, isLast }: { ev: TimelineEvent; isLast: boolean }) {
  const isDoneTask = ev.source === 'task' && ev.status === 'done';
  const style =
    ev.source === 'task' && isDoneTask
      ? { icon: CheckCircle2, dot: 'bg-ok/10 text-ok border-ok/30', label: 'Task' }
      : KIND_STYLE[ev.kind] ?? FALLBACK_STYLE;
  const Icon = style.icon;

  return (
    <li className="relative pl-10 pb-5 last:pb-0">
      {/* connector spine down to the next dot */}
      {!isLast && (
        <span className="absolute left-[13px] top-8 bottom-0 w-px bg-slate/15" aria-hidden />
      )}
      <span
        className={`absolute left-0 top-0 w-7 h-7 rounded-full border flex items-center justify-center ${style.dot}`}
      >
        <Icon className="w-3.5 h-3.5" />
      </span>

      <div className="flex flex-wrap items-baseline gap-x-2 gap-y-0.5">
        <span className="text-[10px] font-label font-semibold uppercase tracking-wide text-slate/40">
          {style.label}
        </span>
        {ev.actor && <span className="text-[10px] text-slate/45">{ev.actor}</span>}
        <span className="text-[10px] text-slate/35 tnum ml-auto">{fmtDateTime(ev.ts)}</span>
      </div>

      <p
        className={`text-sm mt-0.5 ${
          ev.kind === 'error'
            ? 'text-danger'
            : isDoneTask
            ? 'text-slate/50 line-through'
            : 'text-slate/80'
        }`}
      >
        {ev.source === 'note' ? ev.body || ev.title : ev.title}
      </p>

      {/* task meta: due date (red only when overdue AND still open) */}
      {ev.source === 'task' && ev.due_at && (
        <TaskDue due={ev.due_at} open={ev.status === 'open'} />
      )}

      {/* audit events can carry a structured detail payload */}
      {ev.source === 'audit' && ev.detail != null && (
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

function TaskDue({ due, open }: { due: string; open: boolean }) {
  const d = new Date(due);
  const overdue = open && !Number.isNaN(d.getTime()) && d.getTime() < Date.now();
  const label = Number.isNaN(d.getTime())
    ? due
    : d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  return (
    <p className={`text-xs mt-0.5 ${overdue ? 'text-danger font-medium' : 'text-slate/45'}`}>
      Due {label}
      {overdue && ' · overdue'}
    </p>
  );
}

export function DealTimeline({ dealId, refreshKey = 0 }: { dealId: string; refreshKey?: number }) {
  const [data, setData] = useState<DealTimelineResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    getDealTimeline(dealId)
      .then((res) => {
        if (cancelled) return;
        setData(res);
        setLoading(false);
      })
      .catch((e) => {
        if (cancelled) return;
        if (e instanceof ApiError && e.status === 401) return; // handled globally
        setError(e instanceof Error ? e.message : String(e));
        setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [dealId, refreshKey]);

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

  const events = data?.events ?? [];
  const groups = data?.groups ?? [];
  const byId = new Map(events.map((e) => [e.id, e]));

  return (
    <div className="space-y-4">
      <h2 className="eyebrow text-slate/60 flex items-center">
        <History className="w-4 h-4 mr-2" /> Activity
        <span className="ml-2 normal-case font-normal text-xs text-slate/50">
          — runs, notes &amp; tasks in one timeline, newest first
        </span>
      </h2>

      {events.length === 0 ? (
        <Card className="p-8 text-center">
          <p className="text-sm text-slate/60">
            Nothing has happened on this deal yet. Underwrite runs append their trail here, and any
            note or task you pin shows up alongside them.
          </p>
        </Card>
      ) : (
        <div className="space-y-6">
          {groups.map((group) => {
            const groupEvents = group.ids
              .map((id) => byId.get(id))
              .filter((e): e is TimelineEvent => !!e);
            if (groupEvents.length === 0) return null;
            return (
              <div key={group.month}>
                <div className="flex items-center gap-3 mb-4">
                  <h3 className="font-label text-xs font-semibold uppercase tracking-wider text-slate/45">
                    {group.month}
                  </h3>
                  <span className="flex-1 h-px bg-slate/10" aria-hidden />
                  <span className="text-[10px] text-slate/35 tnum">
                    {groupEvents.length} event{groupEvents.length === 1 ? '' : 's'}
                  </span>
                </div>
                <Card className="p-5">
                  <ol>
                    {groupEvents.map((ev, idx) => (
                      <EventRow key={ev.id} ev={ev} isLast={idx === groupEvents.length - 1} />
                    ))}
                  </ol>
                </Card>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
