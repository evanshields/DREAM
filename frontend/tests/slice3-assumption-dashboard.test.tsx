// Slice 3 (plan docs/research/2026-11-04-frontend-test-plan.md). Synthetic data only, fetch stubbed, no live service.
// Vitest + jsdom + React Testing Library. NOT run: no runner is installed on this branch (see PR body).
// it.fails = the app really has this gap today, so the test is expected to fail until the product is fixed.
import { describe, it, expect, vi, afterEach, beforeEach } from 'vitest';
import { render, screen, waitFor, fireEvent, cleanup } from '@testing-library/react';
import { AssumptionDashboard } from '../src/components/AssumptionDashboard';

const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });

beforeEach(() => localStorage.setItem('dream_token', 'test-token'));
afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
  localStorage.clear();
});

describe('F29 main recalc error clears metrics', () => {
  it.fails('F29 shows no stale IRR or multiple after a failed recalc', async () => {
    let recalcCalls = 0;
    vi.stubGlobal(
      'fetch',
      vi.fn(async (url: string) => {
        if (String(url).endsWith('/recalc/sensitivity')) return json({ field: 'exit_cap', metric: 'irr', grid: [] });
        recalcCalls += 1;
        return recalcCalls === 1
          ? json({ headline_metrics: { irr: 0.2, equity_multiple: 2.1 } })
          : json({ detail: 'exit cap must be positive' }, 422);
      }),
    );
    render(<AssumptionDashboard />);
    await screen.findByText(/20\.0%/);
    await screen.findByText(/2\.10x/);

    const field = screen.getAllByLabelText(/exit cap/i)[0];
    fireEvent.change(field, { target: { value: '-1' } });
    fireEvent.blur(field);

    await screen.findByText(/exit cap must be positive/, undefined, { timeout: 3000 });
    // Fail closed: the old numbers must be gone. RED today (metrics state is kept on error).
    expect(screen.queryByText(/20\.0%/)).toBeNull();
    expect(screen.queryByText(/2\.10x/)).toBeNull();
  });
});

describe('F16 null sensitivity points show a dash', () => {
  it('F16 renders a dash, never 0, null or NaN, for a null cell', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(async (url: string) =>
        String(url).endsWith('/recalc/sensitivity')
          ? json({
              field: 'exit_cap',
              metric: 'irr',
              grid: [
                { value: 0.05, result: 0.25 },
                { value: 0.06, result: null },
                { value: 0.07, result: 0.15 },
              ],
            })
          : json({ headline_metrics: { irr: 0.2, equity_multiple: 2.1 } }),
      ),
    );
    render(<AssumptionDashboard />);
    const rows = await screen.findAllByRole('row');
    const nullRow = rows.find((r) => r.textContent?.includes('6.00%'));
    expect(nullRow).toBeDefined();
    const cells = nullRow!.querySelectorAll('td');
    expect(cells[1].textContent).toBe('—');
    expect(nullRow!.textContent).not.toMatch(/NaN|null|undefined/);
    await waitFor(() => expect(cells[1].textContent).not.toBe('0'));
  });
});
