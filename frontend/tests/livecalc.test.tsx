// F14 (plan docs/research/2026-11-04-frontend-test-plan.md): useLiveCalc must
// clear its last good result when a later recalc fails. Synthetic data only.
// Written against Vitest + jsdom + React Testing Library (the plan's proposed
// runner). NOT wired into any script yet: no runner is installed on this branch.
import { describe, it, expect, vi, afterEach } from 'vitest';
import { renderHook, act, cleanup } from '@testing-library/react';
import { useLiveCalc } from '../src/components/livecalc';
import { ApiError } from '../src/lib/api';

afterEach(() => {
  cleanup();
  vi.useRealTimers();
});

describe('F14 useLiveCalc clears result when a recalc fails', () => {
  it('keeps no stale number beside an error', async () => {
    vi.useFakeTimers();
    const fn = vi
      .fn<(req: { cap: number }, signal?: AbortSignal) => Promise<{ irr: number }>>()
      .mockResolvedValueOnce({ irr: 0.2 })
      .mockRejectedValueOnce(new ApiError(422, 'bad input'));

    const { result, rerender } = renderHook(({ req }) => useLiveCalc(fn, req), {
      initialProps: { req: { cap: 0.06 } },
    });

    await act(async () => {
      await vi.advanceTimersByTimeAsync(0);
    });
    expect(result.current.result).toEqual({ irr: 0.2 });
    expect(result.current.error).toBeNull();

    rerender({ req: { cap: -1 } });
    await act(async () => {
      await vi.advanceTimersByTimeAsync(500); // past the 450ms debounce
    });

    expect(result.current.error).toBe('bad input');
    // Fail closed: the old 0.2 must be gone. RED today (hook keeps it).
    expect(result.current.result).toBeNull();
  });
});
