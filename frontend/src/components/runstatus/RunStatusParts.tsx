import type { ReactNode } from 'react';
import { Card, Badge } from '../ui';
import type {
  DisplayState,
  EvidenceState,
  GateStatus,
  RunEvent,
  RunEvidence,
  RunGate,
  RunHeadline,
  RunHold,
  RunView,
} from '../../lib/runStatusApi';

type Tone = 'ok' | 'warn' | 'danger' | 'neutral' | 'teal';

export const STATE_LABEL: Record<DisplayState, string> = {
  failed: 'Failed',
  blocked: 'Blocked',
  stale: 'Out of date',
  in_progress: 'In progress',
  needs_input: 'Needs input',
  needs_human_check: 'Needs human check',
  complete: 'Complete',
};

export const STATE_TONE: Record<DisplayState, Tone> = {
  failed: 'danger',
  blocked: 'danger',
  stale: 'warn',
  in_progress: 'neutral',
  needs_input: 'warn',
  needs_human_check: 'teal',
  complete: 'ok',
};

const GATE_TONE: Record<GateStatus, Tone> = { green: 'ok', amber: 'warn', red: 'danger', not_run: 'neutral', missing: 'danger' };
const GATE_LABEL: Record<GateStatus, string> = { green: 'Green', amber: 'Amber', red: 'Red', not_run: 'Not run', missing: 'Missing' };
const EVIDENCE_TONE: Record<EvidenceState, Tone> = { ok: 'ok', missing: 'danger', hash_mismatch: 'danger' };
const EVIDENCE_LABEL: Record<EvidenceState, string> = {
  ok: 'Verified',
  missing: 'Missing',
  hash_mismatch: 'Fingerprint mismatch',
};

export function StateBadge({ state }: { state: DisplayState }) {
  return <Badge tone={STATE_TONE[state]}>{STATE_LABEL[state]}</Badge>;
}

function Section({ title, children }: { title: string; children: ReactNode }) {
  return (
    <Card className="p-4 mb-4">
      <h2 className="font-heading text-base mb-3">{title}</h2>
      {children}
    </Card>
  );
}

export function StateBanner({ run }: { run: RunView }) {
  const loud = run.display_state === 'blocked' || run.display_state === 'stale' || run.display_state === 'failed';
  const cls = loud
    ? 'border-2 border-danger bg-danger/10 text-danger'
    : 'border border-slate/20 bg-slate/5 text-slate';
  return (
    <div role="status" className={`rounded-lg p-4 mb-4 ${cls}`}>
      <div className="flex items-center gap-2 mb-1">
        <StateBadge state={run.display_state} />
        {run.synthetic && <Badge tone="neutral">Sample data</Badge>}
      </div>
      <p className={loud ? 'font-semibold' : ''}>{run.state_sentence}</p>
      {run.error_message && <p className="mt-1">{run.error_message}</p>}
      {run.is_stale && (
        <p className="mt-1 text-sm">
          Engine {run.engine_commit} vs current {run.current_engine_commit}. Inputs {run.inputs_hash} vs current{' '}
          {run.current_inputs_hash}.
        </p>
      )}
    </div>
  );
}

export function GateList({ gates }: { gates: RunGate[] }) {
  return (
    <Section title="Quality gates">
      {gates.length === 0 ? (
        <p className="text-sm text-slate">No gates recorded.</p>
      ) : (
        <ul className="space-y-2">
          {gates.map((g) => (
            <li key={g.id} className="flex items-start gap-3">
              <Badge tone={GATE_TONE[g.status]}>{GATE_LABEL[g.status]}</Badge>
              <div>
                <div className="font-medium">{g.name}</div>
                <div className="text-sm text-slate">{g.detail}</div>
              </div>
            </li>
          ))}
        </ul>
      )}
    </Section>
  );
}

// Values print exactly as stored. null shows "Blank" plus the reason. 0 shows as 0.
function shown(h: RunHeadline): string {
  return h.value === null ? 'Blank' : `${h.value}`;
}

export function HeadlineList({ items, diagnostic }: { items: RunHeadline[]; diagnostic: boolean }) {
  return (
    <Section title="Headline numbers">
      {diagnostic && (
        <p className="mb-3 text-sm font-semibold text-danger">
          Diagnostic only. These numbers are not a finished result.
        </p>
      )}
      {items.length === 0 ? (
        <p className="text-sm text-slate">No numbers yet.</p>
      ) : (
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-slate">
              <th className="py-1 pr-3">Name</th>
              <th className="py-1 pr-3">Value</th>
              <th className="py-1">Source or reason</th>
            </tr>
          </thead>
          <tbody>
            {items.map((h) => (
              <tr key={h.name} className="border-t border-slate/10 align-top">
                <td className="py-2 pr-3">{h.name}</td>
                <td className="py-2 pr-3">
                  {h.value === null ? (
                    <Badge tone="warn">Blank</Badge>
                  ) : (
                    <span className={diagnostic ? 'italic text-slate' : 'font-semibold'}>
                      {shown(h)} {h.unit}
                    </span>
                  )}
                </td>
                <td className="py-2">
                  {h.value === null ? (
                    <span>{h.blank_reason || 'No reason recorded.'}</span>
                  ) : (
                    <span className="text-slate">
                      {h.source_file} {h.source_pointer}
                    </span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </Section>
  );
}

export function EvidenceList({ items }: { items: RunEvidence[] }) {
  return (
    <Section title="Evidence files">
      {items.length === 0 ? (
        <p className="text-sm text-slate">No evidence files yet.</p>
      ) : (
        <ul className="space-y-2">
          {items.map((e) => (
            <li key={e.path} className="flex items-start gap-3">
              <Badge tone={EVIDENCE_TONE[e.state]}>{EVIDENCE_LABEL[e.state]}</Badge>
              <div>
                <div className="font-medium">{e.name}</div>
                <div className="text-xs text-slate break-all">
                  {e.path} (sha256 {e.sha256})
                </div>
              </div>
            </li>
          ))}
        </ul>
      )}
    </Section>
  );
}

export function HoldList({ holds }: { holds: RunHold[] }) {
  return (
    <Section title="Open holds">
      {holds.length === 0 ? (
        <p className="text-sm text-slate">No open holds.</p>
      ) : (
        <ul className="space-y-2">
          {holds.map((h) => (
            <li key={h.id}>
              {h.reason} <span className="text-sm text-slate">Owner: {h.owner}</span>
            </li>
          ))}
        </ul>
      )}
    </Section>
  );
}

export function EventTimeline({ events }: { events: RunEvent[] }) {
  return (
    <Section title="Timeline">
      {events.length === 0 ? (
        <p className="text-sm text-slate">No events yet.</p>
      ) : (
        <ol className="space-y-1 text-sm">
          {events.map((e) => (
            <li key={`${e.at_utc}-${e.text}`}>
              <span className="text-slate">{e.at_utc}</span> {e.text}
            </li>
          ))}
        </ol>
      )}
    </Section>
  );
}
