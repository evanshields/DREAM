// Slice 3 (plan docs/research/2026-11-04-frontend-test-plan.md). Synthetic data only, fetch stubbed, no live service.
// Vitest + jsdom + React Testing Library. NOT run: no runner is installed on this branch (see PR body).
// it.fails = the app really has this gap today, so the test is expected to fail until the product is fixed.
import { describe, it, expect, vi, afterEach, beforeEach } from 'vitest';
import { render, screen, waitFor, cleanup } from '@testing-library/react';
import App from '../src/App';

const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });

function stubApi(deals: unknown = []) {
  vi.stubGlobal(
    'fetch',
    vi.fn(async (url: string) => {
      const u = String(url);
      if (u.endsWith('/me')) return json({ email: 'test@example.com', name: 'Test User', picture: null });
      if (u.includes('/deals')) return json(deals);
      return json({}, 404);
    }),
  );
}

beforeEach(() => window.history.pushState({}, '', '/nope/nothing'));
afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
  vi.resetModules();
  localStorage.clear();
});

describe('F26 unknown URL goes to pipeline', () => {
  it('F26 with a token an unknown URL lands on /pipeline', async () => {
    localStorage.setItem('dream_token', 'test-token');
    stubApi();
    render(<App />);
    await waitFor(() => expect(window.location.pathname).toBe('/pipeline'));
  });

  it('F26 without a token the same URL ends on /login', async () => {
    stubApi();
    render(<App />);
    await waitFor(() => expect(window.location.pathname).toBe('/login'));
  });
});

describe('F24 error boundary', () => {
  // No ErrorBoundary exists in the app today, so a render error blanks the whole page. Red first.
  it.fails('F24 a render error shows a fallback with a reload hint, not a blank screen', async () => {
    vi.doMock('../src/pages/Pipeline', () => ({
      Pipeline: () => (('x') as any).toFixed(2),
    }));
    vi.spyOn(console, 'error').mockImplementation(() => {});
    localStorage.setItem('dream_token', 'test-token');
    stubApi();
    const { default: FreshApp } = await import('../src/App');
    const { container } = render(<FreshApp />);
    expect(await screen.findByText(/reload/i)).toBeTruthy();
    expect(container.textContent?.trim().length).toBeGreaterThan(0);
  });
});
