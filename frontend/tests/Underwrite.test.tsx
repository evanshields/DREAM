// F04 failed job shows no tiles, F05 submit stays disabled until blocking questions are answered.
// Underwrite starts at the intake form, so each test submits the form against a stubbed /api/jobs.
import { describe, it, expect, vi, afterEach, beforeEach } from 'vitest';
import { render, screen, cleanup, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { Underwrite } from '../src/pages/Underwrite';
import { jsonResponse, stubFetch } from './helpers';

const baseJob = {
  job_id: 'job-1', deal_id: 'deal-test-1', phase: 'x', routing: 'ACQ', mode: 'async',
  cancel_requested: false, error: null, open_questions: [], blocking_questions: [],
};
const q = (id: string, field: string) => ({ id, field, question: `Question ${id}`, blocking: true });

function renderPage() {
  return render(<MemoryRouter><Underwrite /></MemoryRouter>);
}

beforeEach(() => {
  localStorage.setItem('dream_token', 'test-token');
  if (!globalThis.crypto?.randomUUID) {
    vi.stubGlobal('crypto', { randomUUID: () => 'test-key' });
  }
});
afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

describe('F04 failed job', () => {
  it('F04 shows the failed panel and no metric tiles, even when stale metrics ride along', async () => {
    stubFetch([[/POST .*\/jobs$/, () => jsonResponse({
      ...baseJob, status: 'failed', error: 'analyst error', headline_metrics: { irr: 0.2 },
    })]]);
    renderPage();
    await userEvent.click(screen.getByRole('button', { name: /run underwrite/i }));
    expect(await screen.findByText('Underwrite failed')).toBeTruthy();
    expect(screen.getByText('analyst error')).toBeTruthy();
    expect(screen.queryByText(/20\.00%/)).toBeNull();
  });
});

describe('F05 blocking questions gate the submit button', () => {
  async function openQuestions() {
    const fetchSpy = stubFetch([
      [/POST .*\/jobs$/, () => jsonResponse({
        ...baseJob, status: 'awaiting_input',
        blocking_questions: [q('q1', 'exit_cap'), q('q2', 'hold_years')],
      })],
      [/POST .*\/answer$/, () => jsonResponse({ ...baseJob, status: 'running' })],
    ]);
    renderPage();
    await userEvent.click(screen.getByRole('button', { name: /run underwrite/i }));
    await screen.findByText('A few inputs needed');
    const button = () => screen.getByRole('button', { name: /submit & resume/i }) as HTMLButtonElement;
    return { fetchSpy, button, cap: screen.getByLabelText(/Question q1/), hold: screen.getByLabelText(/Question q2/) };
  }

  it('F05 is disabled when blank and when only one of two is answered', async () => {
    const { button, cap } = await openQuestions();
    expect(button().disabled).toBe(true);
    await userEvent.type(cap, '6');
    expect(button().disabled).toBe(true);
  });

  it('F05 is enabled when both answers are numbers and posts exactly those numbers', async () => {
    const { fetchSpy, button, cap, hold } = await openQuestions();
    await userEvent.type(cap, '6');
    await userEvent.type(hold, '5');
    expect(button().disabled).toBe(false);
    await userEvent.click(button());
    await waitFor(() => {
      const bodies = fetchSpy.mock.calls
        .filter(([u]) => String(u).endsWith('/answer'))
        .map(([, init]) => JSON.parse(String(init?.body)));
      expect(bodies).toEqual([
        { question_id: 'q1', answer: 0.06 }, // exit_cap is typed as a percent, sent as a decimal
        { question_id: 'q2', answer: 5 },
      ]);
    });
  });

  // Real gap: the panel only checks for non-blank text, so these enable the button today.
  it.fails('F05 is disabled for a non-numeric answer (abc)', async () => {
    const { button, cap, hold } = await openQuestions();
    await userEvent.type(cap, '6');
    await userEvent.type(hold, 'abc');
    expect(button().disabled).toBe(true);
  });

  it.fails('F05 is disabled for Infinity', async () => {
    const { button, cap, hold } = await openQuestions();
    await userEvent.type(cap, '6');
    await userEvent.type(hold, 'Infinity');
    expect(button().disabled).toBe(true);
  });
});
