// F13 (plan docs/research/2026-11-04-frontend-test-plan.md, section 5): useJobPolling stops after
// three failures in a row and reports once, a success resets the count, terminal statuses stop
// polling and running statuses keep it going. Synthetic data only, fetch is stubbed. Written
// against Vitest + jsdom + React Testing Library (the plan's proposed runner). NOT wired into any
// script yet: no runner is installed on this branch, so these have not been executed.
import { describe, it, expect, vi, afterEach, beforeEach } from 'vitest';
import { renderHook, act, cleanup } from '@testing-library/react';
import { useJobPolling, RUNNING_STATUSES } from '../src/hooks/useJobPolling';

const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });

const view = (status: string) => ({
  job_id: 'job-1',
  deal_id: 'deal-1',
  status,
  phase: 'x',
  routing: 'ACQ',
  mode: 'HITL',
  cancel_requested: false,
  error: null,
  open_questions: [],
  blocking_questions: [],
});

beforeEach(() => vi.useFakeTimers());
afterEach(() => {
  cleanup();
  vi.useRealTimers();
  vi.unstubAllGlobals();
});

// First tick at 300ms, later ticks every 2500ms while running.
async function advance(ms: number) {
  await act(async () => {
    await vi.advanceTimersByTimeAsync(ms);
  });
}

function host(fetchFn: ReturnType<typeof vi.fn>) {
  vi.stubGlobal('fetch', fetchFn);
  const onUpdate = vi.fn();
  const onError = vi.fn();
  renderHook(() => useJobPolling('job-1', onUpdate, onError));
  return { onUpdate, onError };
}

describe('F13 useJobPolling', () => {
  it('reports once after three failures in a row and makes no fourth fetch', async () => {
    const fetchFn = vi.fn(async () => json({ detail: 'boom' }, 500));
    const { onError, onUpdate } = host(fetchFn);

    await advance(300); // failure 1
    await advance(2500); // failure 2
    expect(onError).not.toHaveBeenCalled();
    await advance(2500); // failure 3
    expect(fetchFn).toHaveBeenCalledTimes(3);
    expect(onError).toHaveBeenCalledTimes(1);
    expect(onError.mock.calls[0][0]).toContain('Lost contact with the underwrite run');

    await advance(20_000); // four more intervals, nothing should fire
    expect(fetchFn).toHaveBeenCalledTimes(3);
    expect(onError).toHaveBeenCalledTimes(1);
    expect(onUpdate).not.toHaveBeenCalled();
  });

  it('also counts rejected fetches as failures', async () => {
    const fetchFn = vi.fn(async () => {
      throw new TypeError('offline');
    });
    const { onError } = host(fetchFn);
    await advance(300 + 2500 + 2500 + 10_000);
    expect(fetchFn).toHaveBeenCalledTimes(3);
    expect(onError).toHaveBeenCalledTimes(1);
    expect(onError.mock.calls[0][0]).toContain('offline');
  });

  it('a success between failures resets the count', async () => {
    const fetchFn = vi
      .fn()
      .mockResolvedValueOnce(json({ detail: 'x' }, 500))
      .mockResolvedValueOnce(json({ detail: 'x' }, 500))
      .mockResolvedValueOnce(json(view('analyzing')))
      .mockResolvedValueOnce(json({ detail: 'x' }, 500))
      .mockResolvedValueOnce(json({ detail: 'x' }, 500))
      .mockResolvedValueOnce(json(view('completed')));
    const { onError, onUpdate } = host(fetchFn);

    await advance(300 + 2500 * 5);
    expect(fetchFn).toHaveBeenCalledTimes(6);
    expect(onError).not.toHaveBeenCalled();
    expect(onUpdate).toHaveBeenCalledTimes(2);
  });

  it.each(['failed', 'cancelled', 'awaiting_cp1', 'awaiting_input', 'completed'])('stops after a terminal status: %s', async (status) => {
    const fetchFn = vi.fn(async () => json(view(status)));
    const { onUpdate, onError } = host(fetchFn);

    await advance(300);
    expect(onUpdate).toHaveBeenCalledTimes(1);
    await advance(30_000);
    expect(fetchFn).toHaveBeenCalledTimes(1);
    expect(onError).not.toHaveBeenCalled();
  });

  it.each([...RUNNING_STATUSES])('keeps polling while status is %s', async (status) => {
    const fetchFn = vi.fn(async () => json(view(status)));
    const { onUpdate } = host(fetchFn);

    await advance(300 + 2500 * 3);
    expect(fetchFn.mock.calls.length).toBeGreaterThanOrEqual(4);
    expect(onUpdate.mock.calls.length).toBeGreaterThanOrEqual(4);
  });
});
