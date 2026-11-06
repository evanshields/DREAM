// Slice 3 (plan docs/research/2026-11-04-frontend-test-plan.md). Synthetic data only, fetch stubbed, no live service.
// Vitest + jsdom + React Testing Library. NOT run: no runner is installed on this branch (see PR body).
// it.fails = the app really has this gap today, so the test is expected to fail until the product is fixed.
import { describe, it, expect, vi, afterEach, beforeEach } from 'vitest';
import { render, screen, cleanup } from '@testing-library/react';
import { BondScreen } from '../src/pages/BondScreen';

const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });

beforeEach(() => localStorage.setItem('dream_token', 'test-token'));
afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
  localStorage.clear();
});

describe('F18 null max loan shows a dash', () => {
  // Note: the plan names the EFB response, but max_loan is read in the Agency Takeout panel
  // (/recalc/agency-sizing), so that endpoint is mocked. Other panels get a 500 and show their own error.
  it('F18 max loan tile is a dash while the constraint rows keep their numbers', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(async (url: string) =>
        String(url).endsWith('/recalc/agency-sizing')
          ? json({ max_loan: null, binding_constraint: 'dscr', by_dscr: 5000000, by_ltv: 6000000, by_debt_yield: 7000000 })
          : json({ detail: 'not mocked' }, 500),
      ),
    );
    render(<BondScreen />);
    await screen.findByText('$5,000,000');
    expect(screen.getByText('$6,000,000')).toBeTruthy();
    expect(screen.getByText('$7,000,000')).toBeTruthy();
    const heading = screen.getByText(/Agency Takeout Sizing/);
    const card = heading.closest('div')!.parentElement!.parentElement!;
    // The big max-loan number is the only text-4xl element in the card.
    const tile = card.querySelector('.text-4xl') as HTMLElement;
    expect(tile.textContent).toBe('—');
    // textContent joins neighbours with no space, so a bare word boundary after $0 would miss "$0Binding".
    expect(card.textContent).not.toMatch(/\$0(?![0-9,])|NaN|null|undefined/);
  });
});
