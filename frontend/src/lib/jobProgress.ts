import type { JobView } from './api';

export const RUNNING_STATUSES = new Set(['submitted', 'routing', 'analyzing', 'synthesizing']);
const TERMINAL_STATUSES = new Set(['awaiting_cp1', 'completed', 'failed', 'cancelled']);
const KNOWN_STATUSES = new Set([...RUNNING_STATUSES, ...TERMINAL_STATUSES, 'awaiting_input']);
const PHASE_RANK: Record<string, number> = { submitted: 0, routing: 1, analyzing: 2, synthesizing: 3 };

export function isKnownJobStatus(job: JobView): boolean {
  return KNOWN_STATUSES.has(job.status);
}

// A cancel request is only an acknowledgement. The server must report the outcome.
export function isCancellationPending(job: JobView): boolean {
  return job.cancel_requested && RUNNING_STATUSES.has(job.status);
}

export function shouldPollJob(job: JobView): boolean {
  return RUNNING_STATUSES.has(job.status) || !isKnownJobStatus(job);
}

export type RunDestination = 'running' | 'questions' | 'failed' | 'review' | 'intake';

export function runDestination(job: JobView): RunDestination {
  if (job.status === 'cancelled') return 'intake';
  if (job.status === 'failed') return 'failed';
  if (isCancellationPending(job)) return 'running';
  if (job.status === 'awaiting_cp1' || job.status === 'completed') return 'review';
  if (job.status === 'awaiting_input') return 'questions';
  return 'running';
}

export async function requestJobCancellation(
  jobId: string,
  cancel: (id: string, signal?: AbortSignal) => Promise<JobView>,
  apply: (view: JobView) => void,
  signal?: AbortSignal,
): Promise<void> {
  // Keep the current run on screen if the request fails; never synthesize cancellation.
  const view = await cancel(jobId, signal);
  if (!signal?.aborted) apply(view);
}

export function mergeJobView(current: JobView | null, incoming: JobView): JobView {
  if (!current) return incoming;
  if (current.job_id !== incoming.job_id) return current;
  if (TERMINAL_STATUSES.has(current.status)) return current;
  if (RUNNING_STATUSES.has(current.status) && RUNNING_STATUSES.has(incoming.status) && PHASE_RANK[incoming.status] < PHASE_RANK[current.status]) {
    // An older phase can still carry a newer cancellation acknowledgement.
    // Keep phase ordering while preserving the monotonic request bit.
    return incoming.cancel_requested && !current.cancel_requested
      ? { ...current, cancel_requested: true }
      : current;
  }
  return { ...incoming, cancel_requested: current.cancel_requested || incoming.cancel_requested };
}
