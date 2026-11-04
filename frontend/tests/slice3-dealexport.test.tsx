// Slice 3 (plan docs/research/2026-11-04-frontend-test-plan.md). Synthetic data only, fetch stubbed, no live service.
// Vitest + jsdom + React Testing Library. NOT run: no runner is installed on this branch (see PR body).
// it.fails = the app really has this gap today, so the test is expected to fail until the product is fixed.
import { describe, it, expect, vi, afterEach } from 'vitest';
import { render, screen, cleanup, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import * as download from '../src/lib/download';
import { DealExport } from '../src/components/DealExport';

const XLSX = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';
const report = (refusals: Record<string, unknown>) => ({
  ok: false, written: [], written_count: 3, identity_blocked: false, structural_diff_ok: true,
  structural_diff_detail: {}, missing_cells: [], patches_applied: [], patch_log: [], draft_path: '',
  refusals: { formula: [], fee_bounds: [], unit_count: [], ltv: [], rubs: [], exit_cap: [], ...refusals },
});
const jsonRes = (body: unknown) =>
  new Response(JSON.stringify(body), { status: 200, headers: { 'Content-Type': 'application/json' } });

async function exportWith(res: Response) {
  vi.stubGlobal('fetch', vi.fn(async () => res));
  const utils = render(<DealExport dealId="deal-test-1" />);
  const input = utils.container.querySelector('input[type=file]') as HTMLInputElement;
  await userEvent.upload(input, new File(['x'], 'template.xlsx', { type: XLSX }));
  await userEvent.click(screen.getByRole('button', { name: /export to excel/i }));
  return utils;
}

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
});

describe('F20 refusal groups always visible', () => {
  // Plan shape adapted to the real report: groups are formula, fee_bounds, unit_count, ltv, rubs, exit_cap.
  // Gap today: the formula group sits inside a closed <details>, so it is hidden until clicked.
  it.fails('F20 every refusal line is visible with no click and there is no collapse control', async () => {
    const { container } = await exportWith(
      jsonRes(report({
        formula: [{ cell: 'B7', existing: '=SUM(A1:A3)' }],
        fee_bounds: [{ cell: 'C4', reason: 'fee above bound' }],
        unit_count: ['S12'],
        ltv: ['D9'],
      })),
    );
    await screen.findByText(/Populate completed with refusals/);
    expect(screen.getByText('S12')).toBeVisible();
    expect(screen.getByText('D9')).toBeVisible();
    expect(screen.getByText(/B7/)).toBeVisible();
    expect(screen.getByText(/fee above bound/)).toBeVisible();
    expect(container.querySelector('summary')).toBeNull();
    expect(screen.queryByRole('button', { name: /download/i })).toBeNull();
  });
});

describe('F28 export does not save error JSON as a workbook', () => {
  it('F28 a JSON report is shown and downloadBlob is never called', async () => {
    const spy = vi.spyOn(download, 'downloadBlob').mockImplementation(() => {});
    await exportWith(jsonRes(report({ unit_count: ['S12'] })));
    await screen.findByText(/Populate completed with refusals/);
    expect(spy).toHaveBeenCalledTimes(0);
  });

  it('F28 an xlsx body is downloaded once with an .xlsx filename', async () => {
    const spy = vi.spyOn(download, 'downloadBlob').mockImplementation(() => {});
    await exportWith(
      new Response(new Blob(['PK']), {
        status: 200,
        headers: { 'Content-Type': XLSX, 'Content-Disposition': 'attachment; filename="deal-test-1.xlsx"' },
      }),
    );
    await waitFor(() => expect(spy).toHaveBeenCalledTimes(1));
    expect(String(spy.mock.calls[0][1])).toMatch(/\.xlsx$/);
  });
});
