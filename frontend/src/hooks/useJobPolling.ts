// useJobPolling — drives a running fast-path job to a terminal (non-running) status by
// polling GET /api/jobs/{id}. Async-mode submit/answer now return immediately with a
// "submitted"/"routing" body (no 20s–4min block), so the UI polls the job forward instead.
//
// Design notes:
//   * setTimeout-CHAINED ticks (never overlapping setInterval): each tick schedules the next
//     only AFTER its fetch settles, so a slow response can't stack requests.
//   * Cadence: first tick ~300ms (near-immediate), then 2500ms, easing to 5000ms once 60s have
//     elapsed since polling started.
//   * A fresh AbortController per request; cleanup (clear timer + abort) on unmount and on
//     jobId change. Delivers EVERY view via onUpdate; stops itself permanently once the returned
//     status is NOT running (after delivering that final view).
//   * Tolerates up to 3 CONSECUTIVE fetch failures (reset on success) before calling onError and
//     stopping; AbortErrors are ignored (they are our own cancellations, not failures).
//   * Refs hold the latest onUpdate/onError so those callbacks changing does NOT restart polling.
import { useEffect, useRef } from 'react';
import { getJob, type JobView } from '../lib/api';

// Statuses that mean the run is still in flight — keep polling. Everything else is terminal
// for the poller (awaiting_input / awaiting_cp1 / completed / failed / cancelled), so we stop
// after delivering that view and let the caller route it.
export const RUNNING_STATUSES = new Set(['submitted', 'routing', 'analyzing', 'synthesizing']);

const FIRST_DELAY_MS = 300;
const FAST_INTERVAL_MS = 2500;
const SLOW_INTERVAL_MS = 5000;
const EASE_AFTER_MS = 60_000;
const MAX_CONSECUTIVE_FAILURES = 3;

export function useJobPolling(
  jobId: string | null,
  onUpdate: (view: JobView) => void,
  onError?: (message: string) => void,
): void {
  // Keep the latest callbacks in refs so re-renders that pass new function identities don't
  // retrigger the polling effect (which would reset the cadence + failure counter).
  const onUpdateRef = useRef(onUpdate);
  const onErrorRef = useRef(onError);
  onUpdateRef.current = onUpdate;
  onErrorRef.current = onError;

  useEffect(() => {
    if (!jobId) return; // null jobId disables polling entirely.

    let stopped = false;
    let timer: number | null = null;
    let ctrl: AbortController | null = null;
    let failures = 0;
    const startedAt = Date.now();

    const stop = () => {
      stopped = true;
      if (timer !== null) {
        window.clearTimeout(timer);
        timer = null;
      }
      ctrl?.abort();
    };

    const schedule = (delay: number) => {
      if (stopped) return;
      timer = window.setTimeout(tick, delay);
    };

    const tick = async () => {
      if (stopped) return;
      ctrl = new AbortController();
      try {
        const view = await getJob(jobId, ctrl.signal);
        if (stopped) return;
        failures = 0; // any success resets the tolerance window.
        onUpdateRef.current(view); // deliver EVERY view, including the final one.
        if (!RUNNING_STATUSES.has(view.status)) {
          stop(); // terminal for the poller — the caller routes it from here.
          return;
        }
        // ease the cadence once the run has been going a while.
        const elapsed = Date.now() - startedAt;
        schedule(elapsed >= EASE_AFTER_MS ? SLOW_INTERVAL_MS : FAST_INTERVAL_MS);
      } catch (err) {
        if (stopped) return;
        // our own aborts (unmount / jobId change) are not failures — swallow them.
        if (err instanceof DOMException && err.name === 'AbortError') return;
        if (err instanceof Error && err.name === 'AbortError') return;
        failures += 1;
        if (failures >= MAX_CONSECUTIVE_FAILURES) {
          const msg = err instanceof Error ? err.message : String(err);
          onErrorRef.current?.(`Lost contact with the underwrite run: ${msg}`);
          stop();
          return;
        }
        // transient — retry on the fast cadence.
        schedule(FAST_INTERVAL_MS);
      }
    };

    schedule(FIRST_DELAY_MS); // first tick is near-immediate.

    return stop; // cleanup on unmount / jobId change.
  }, [jobId]);
}
