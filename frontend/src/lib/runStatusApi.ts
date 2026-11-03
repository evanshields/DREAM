// Typed GET-only client for the read-only run status endpoints. Never sends anything but GET.
import { API_BASE, ApiError, getAuthToken } from './api';

export type GateStatus = 'green' | 'amber' | 'red' | 'not_run';
export type EvidenceState = 'ok' | 'missing' | 'hash_mismatch';
export type DisplayState =
  | 'failed'
  | 'blocked'
  | 'stale'
  | 'in_progress'
  | 'needs_input'
  | 'needs_human_check'
  | 'complete';

export interface RunSummary {
  run_id: string;
  deal_label: string;
  display_state: DisplayState;
  synthetic: boolean;
}

export interface RunGate {
  id: string;
  name: string;
  status: GateStatus;
  detail: string;
}

export interface RunHeadline {
  name: string;
  value: string | number | null;
  unit: string;
  blank_reason: string | null;
  source_file: string | null;
  source_pointer: string | null;
}

export interface RunEvidence {
  name: string;
  path: string;
  sha256: string;
  state: EvidenceState;
}

export interface RunHold {
  id: string;
  reason: string;
  owner: string;
}

export interface RunEvent {
  at_utc: string;
  text: string;
}

export interface RunView {
  run_id: string;
  synthetic: boolean;
  deal_label: string;
  route: string;
  status: string;
  phase: string;
  engine_commit: string;
  current_engine_commit: string;
  inputs_hash: string;
  current_inputs_hash: string;
  gates: RunGate[];
  headline: RunHeadline[];
  evidence: RunEvidence[];
  holds: RunHold[];
  events: RunEvent[];
  error_message?: string;
  display_state: DisplayState;
  state_sentence: string;
  values_are_diagnostic: boolean;
  missing_value_count: number;
  red_gate_count: number;
  is_stale: boolean;
  read_only: boolean;
}

async function getJson<T>(path: string, signal?: AbortSignal): Promise<T> {
  const headers: Record<string, string> = {};
  const token = getAuthToken();
  if (token) headers['Authorization'] = `Bearer ${token}`;
  const res = await fetch(`${API_BASE}${path}`, { method: 'GET', headers, signal });
  if (!res.ok) {
    throw new ApiError(res.status, res.status === 404 ? 'Run not found.' : `Request failed (${res.status}).`);
  }
  return (await res.json()) as T;
}

export async function listRunStatus(signal?: AbortSignal): Promise<RunSummary[]> {
  const body = await getJson<{ runs: RunSummary[] }>('/run-status', signal);
  return body.runs;
}

export function getRunStatus(runId: string, signal?: AbortSignal): Promise<RunView> {
  return getJson<RunView>(`/run-status/${encodeURIComponent(runId)}`, signal);
}
