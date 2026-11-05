// F11 and F12 (plan docs/research/2026-11-04-frontend-test-plan.md, section 7): Pipeline
// attention column, fetch failure and empty list. F10 is HOLD in the plan and is skipped here.
// Synthetic data only, fetch is stubbed, no live service. Written against Vitest + jsdom + React
// Testing Library (the plan's proposed runner). NOT wired into any script yet: no runner is
// installed on this branch, so these have not been executed.
import { describe, it, expect, vi, afterEach, beforeEach } from 'vitest';
import { render, screen, within, waitFor, cleanup } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';

vi.mock('../src/auth/AuthContext', () => ({
  useAuth: () => ({ user: { email: 'tester@example.test' } }),
}));
vi.mock('../src/contexts/ToastContext', () => ({
  useToast: () => ({ showToast: vi.fn() }),
}));

import { Pipeline } from '../src/pages/Pipeline';

function deal(id: string, name: string, status: string, extra: Record<string, unknown> = {}) {
  return {
    deal_id: id,
    deal_name: name,
    slug: id,
    routing: 'ACQ',
    mode: 'HITL',
    status,
    owner: 'tester@example.test',
    version: 1,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-02T00:00:00Z',
    headline_metrics: {},
    ...extra,
  };
}

function stubDeals(handler: () => Response | Promise<Response>) {
  const fn = vi.fn(async () => handler());
  vi.stubGlobal('fetch', fn);
  return fn;
}

const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });

function setView(view: 'cards' | 'table' | 'kanban', preset = 'all') {
  localStorage.setItem(
    'dream_pipeline_view',
    JSON.stringify({ view, preset, sortField: 'updated_at', sortDir: 'desc' }),
  );
}

function renderPipeline() {
  return render(
    <MemoryRouter>
      <Pipeline />
    </MemoryRouter>,
  );
}

beforeEach(() => localStorage.clear());
afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
  localStorage.clear();
});

function column(label: string): HTMLElement {
  // The column root is the ancestor that holds the heading label and its cards.
  // A card badge can carry the same text as a column heading, so keep only the span that sits in
  // the column header row (its parent is the justify-between row, not a card link).
  const heading = screen
    .getAllByText(label, { selector: 'span' })
    .filter((el) => el.parentElement?.classList.contains('justify-between') && !el.closest('a'));
  expect(heading).toHaveLength(1);
  return heading[0].parentElement!.parentElement as HTMLElement;
}

describe('F11 Pipeline attention column', () => {
  const deals = [
    deal('d-gf', 'Gate Failed Deal', 'gate_failed'),
    deal('d-f', 'Failed Deal', 'failed'),
    deal('d-c', 'Cancelled Deal', 'cancelled'),
    deal('d-ok', 'Computed Deal', 'computed'),
  ];

  it('kanban puts gate_failed, failed and cancelled in the attention column only', async () => {
    setView('kanban');
    stubDeals(() => json(deals));
    renderPipeline();

    await screen.findByText('Gate Failed Deal');
    const attention = within(column('Gate Failed'));
    expect(attention.getByText('Gate Failed Deal')).toBeTruthy();
    expect(attention.getByText('Failed Deal')).toBeTruthy();
    expect(attention.getByText('Cancelled Deal')).toBeTruthy();
    expect(attention.queryByText('Computed Deal')).toBeNull();

    const computed = within(column('Computed'));
    expect(computed.getByText('Computed Deal')).toBeTruthy();
    expect(computed.queryByText('Failed Deal')).toBeNull();
  });

  // F11 gap: the "Needs Attention" preset in cards and table view only matches gate_failed and
  // awaiting_input, so failed and cancelled deals the kanban flags are missing from it.
  // RED today. Remove .fails when the preset covers failed and cancelled.
  it('Needs Attention preset renders the gate failed deal and hides computed ones', async () => {
    setView('cards', 'needs_attention');
    stubDeals(() => json(deals));
    renderPipeline();

    await screen.findByText('Gate Failed Deal');
    expect(screen.queryByText('Computed Deal')).toBeNull();
  });

  // The expected failure covers only the two assertions that are red today, so a render crash
  // or a timeout above can no longer hide behind it.
  it.fails('F11 gap: Needs Attention preset lists failed and cancelled deals too', async () => {
    setView('cards', 'needs_attention');
    stubDeals(() => json(deals));
    renderPipeline();

    await screen.findByText('Gate Failed Deal');
    expect(screen.queryByText('Failed Deal')).not.toBeNull();
    expect(screen.queryByText('Cancelled Deal')).not.toBeNull();
  });
});

describe('F12 Pipeline fetch failure and empty list', () => {
  it('shows the error banner and no cards when the fetch rejects', async () => {
    setView('cards');
    stubDeals(() => Promise.reject(new TypeError('network down')));
    renderPipeline();

    await screen.findByText(/network down/);
    expect(screen.queryByText('No deals yet')).toBeNull();
    expect(screen.queryAllByRole('link', { name: /Deal/ })).toHaveLength(0);
  });

  it('shows the error banner when the server answers 500', async () => {
    setView('cards');
    stubDeals(() => json({ detail: 'server blew up' }, 500));
    renderPipeline();

    await screen.findByText(/server blew up/);
    expect(screen.queryByText('No deals yet')).toBeNull();
  });

  it('shows the empty text for an empty list', async () => {
    setView('cards');
    stubDeals(() => json([]));
    renderPipeline();

    await screen.findByText('No deals yet');
    expect(screen.queryByText(/network down|server blew up/)).toBeNull();
    await waitFor(() => expect(screen.getByText('0 active deals')).toBeTruthy());
  });
});
