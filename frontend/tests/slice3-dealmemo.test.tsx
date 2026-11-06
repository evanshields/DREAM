// Slice 3 (plan docs/research/2026-11-04-frontend-test-plan.md). Synthetic data only, fetch stubbed, no live service.
// Vitest + jsdom + React Testing Library. NOT run: no runner is installed on this branch (see PR body).
// it.fails = the app really has this gap today, so the test is expected to fail until the product is fixed.
import { describe, it, expect, vi, afterEach } from 'vitest';
import { render, screen, cleanup } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { DealMemo } from '../src/components/DealMemo';

const json = (body: unknown, status: number) =>
  new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });
afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

describe('F19 memo errors and precedence', () => {
  it('F19 409 shows the not-computed message and no memo', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => json({ detail: 'not computed' }, 409)));
    render(<DealMemo dealId="deal-test-1" dealName="Test Deal" memo={null} />);
    await userEvent.click(screen.getByRole('button', { name: /generate memo/i }));
    expect(await screen.findByText(/has to reach CP-1 first/)).toBeTruthy();
    expect(screen.getByText(/not computed/)).toBeTruthy();
    expect(screen.queryByText('Generated draft')).toBeNull();
  });

  it('F19 502 shows the failure message and no memo', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => json({ detail: 'upstream down, retry' }, 502)));
    render(<DealMemo dealId="deal-test-1" dealName="Test Deal" memo={null} />);
    await userEvent.click(screen.getByRole('button', { name: /generate memo/i }));
    expect(await screen.findByText('Memo generation failed.')).toBeTruthy();
    expect(screen.getByText(/retry/)).toBeTruthy();
    expect(screen.queryByText('Generated draft')).toBeNull();
  });

  it('F19 a fresh 200 memo wins over the stored one', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(async () => json({ memo_markdown: 'generated', generated_at: '2026-11-04T00:00:00Z' }, 200)),
    );
    render(
      <DealMemo
        dealId="deal-test-1"
        dealName="Test Deal"
        memo={{ markdown: 'stored', generated_at: '2026-11-03T00:00:00Z' }}
      />,
    );
    expect(screen.getByText('stored')).toBeTruthy();
    await userEvent.click(screen.getByRole('button', { name: /regenerate/i }));
    expect(await screen.findByText('generated')).toBeTruthy();
    expect(screen.queryByText('stored')).toBeNull();
  });

  it('F19 no memo shows the empty text', () => {
    render(<DealMemo dealId="deal-test-1" dealName="Test Deal" memo={null} />);
    expect(screen.getByText(/No memo on file for this deal yet/)).toBeTruthy();
  });
});
