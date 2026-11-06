import { useEffect, useRef, useState } from 'react';
import { cancelMonoJob, getMonoJob, monoError, type MonoJob } from '../lib/monoApi';

export function monoJobTerminal(state: string): boolean {
  return ['complete', 'completed', 'failed', 'cancelled', 'canceled', 'interrupted', 'timed_out', 'blocked', 'stale', 'stalled', 'rejected'].includes(state.toLowerCase());
}

// Poll only the server-selected job. A generation and abort signal prevent a late
// response from a previous deal or job from replacing the current observation.
export function useMonoJob(dealId: string, seed: MonoJob | null, onTerminal: () => void) {
  const [job, setJob] = useState<MonoJob | null>(seed);
  const [connectionError, setConnectionError] = useState<string | null>(null);
  const [cancelPending, setCancelPending] = useState(false);
  const [clock, setClock] = useState(Date.now());
  const [reconnect, setReconnect] = useState(0);
  const generation = useRef(0);
  const terminalCallback = useRef(onTerminal);
  terminalCallback.current = onTerminal;
  const jobId = seed?.job_id;

  useEffect(() => {
    setJob(seed);
  }, [seed]);

  useEffect(() => {
    const currentGeneration = ++generation.current;
    const controller = new AbortController();
    let timer: ReturnType<typeof setTimeout> | undefined;
    let terminalNotified = false;
    setJob(seed);
    setConnectionError(null);
    setCancelPending(false);
    if (!jobId || !seed || monoJobTerminal(seed.state)) return () => controller.abort();
    const poll = async () => {
      try {
        const next = await getMonoJob(dealId, jobId, controller.signal);
        if (controller.signal.aborted || currentGeneration !== generation.current) return;
        setJob(next);
        setConnectionError(null);
        if (monoJobTerminal(next.state)) {
          setCancelPending(false);
          if (!terminalNotified) { terminalNotified = true; terminalCallback.current(); }
          return;
        }
      } catch (error) {
        if (controller.signal.aborted || currentGeneration !== generation.current) return;
        setConnectionError(monoError(error));
      }
      timer = setTimeout(() => { void poll(); }, 2500);
    };
    void poll();
    return () => { controller.abort(); if (timer) clearTimeout(timer); generation.current += 1; };
    // A refreshed seed is consumed above without restarting a healthy poll loop.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [dealId, jobId, reconnect]);

  useEffect(() => {
    if (!job || monoJobTerminal(job.state)) return;
    const timer = setInterval(() => setClock(Date.now()), 1000);
    return () => clearInterval(timer);
  }, [job?.job_id, job?.state]);

  const cancel = async () => {
    if (!job || monoJobTerminal(job.state) || cancelPending) return;
    const expectedGeneration = generation.current;
    setCancelPending(true);
    try {
      const next = await cancelMonoJob(dealId, job.job_id);
      if (expectedGeneration !== generation.current) return;
      setJob(next);
      if (monoJobTerminal(next.state)) {
        // A poll sent before this cancellation response must not put the job
        // back into a running state after terminal cancellation is confirmed.
        generation.current += 1;
        setCancelPending(false);
        terminalCallback.current();
      }
    } catch (error) {
      if (expectedGeneration !== generation.current) return;
      setConnectionError(monoError(error));
      setCancelPending(false);
    }
  };

  // Elapsed display is timing only. Financial values always remain server-owned.
  const createdAt = job ? Date.parse(job.created_at) : NaN;
  const elapsed = job ? Math.max(0, Math.floor(!monoJobTerminal(job.state) && Number.isFinite(createdAt)
    ? Math.max(job.elapsed_seconds, (clock - createdAt) / 1000) : job.elapsed_seconds)) : 0;
  return { job, elapsed, connectionError, cancelPending, cancel, reconnect: () => setReconnect((n) => n + 1) };
}
