// F09 stored spec seeds only finite numbers. Heavy children are stubbed, the dashboard stub
// records the seed prop it receives. F06, F07, F08 are HOLD in the gap map and not covered here.
import { describe, it, expect, vi, afterEach, beforeEach } from 'vitest';
import { render, screen, cleanup, waitFor } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { DealDetail } from '../src/pages/DealDetail';
import { jsonResponse, stubFetch } from './helpers';

let lastSeed: unknown = 'unset';
vi.mock('../src/components/AssumptionDashboard', () => ({
  AssumptionDashboard: ({ seed }: { seed?: unknown }) => {
    lastSeed = seed;
    return <div>dashboard stub</div>;
  },
}));
vi.mock('../src/components/DealMemo', () => ({ DealMemo: () => <div /> }));
vi.mock('../src/components/DealTimeline', () => ({ DealTimeline: () => <div /> }));
vi.mock('../src/components/DealRail', () => ({ DealRail: () => <div /> }));
vi.mock('../src/components/DealExport', () => ({ DealExport: () => <div /> }));

const deal = (engine_inputs: unknown) => ({
  deal_id: 'deal-test-1', deal_name: 'Test Deal', status: 'computed', routing: 'ACQ',
  headline_metrics: {}, gate_summary: {}, job: null,
  spec: { engine_inputs },
});

function renderDeal(engineInputs: unknown) {
  stubFetch([[/GET .*\/deals\/deal-test-1$/, () => jsonResponse(deal(engineInputs))]]);
  return render(
    <MemoryRouter initialEntries={['/deal/deal-test-1']}>
      <Routes><Route path="/deal/:id" element={<DealDetail />} /></Routes>
    </MemoryRouter>,
  );
}

beforeEach(() => {
  lastSeed = 'unset';
  localStorage.setItem('dream_token', 'test-token');
});
afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

describe('F09 stored spec seeds only finite numbers', () => {
  it('F09 drops a null scalar and any series holding a non-number', async () => {
    renderDeal({ exit_cap: null, purchase_price: 1000000, noi_series: [1, 'x', null, 3], gpr_series: [1, 2, 3] });
    await screen.findByText('dashboard stub');
    await waitFor(() => expect(lastSeed).not.toBe('unset'));
    const seed = lastSeed as Record<string, unknown>;
    expect(seed).not.toHaveProperty('exit_cap');
    expect(seed).not.toHaveProperty('noi_series'); // whole bad series dropped
    expect(seed.gpr_series).toEqual([1, 2, 3]);
    expect(JSON.stringify(seed)).not.toMatch(/NaN|null/);
  });
});
