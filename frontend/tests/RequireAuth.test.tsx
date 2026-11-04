// F01 RequireAuth redirects without a token (plan docs/research/2026-11-04-frontend-test-plan.md).
import { describe, it, expect, vi, afterEach, beforeEach } from 'vitest';
import { render, screen, cleanup, act } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from '../src/auth/AuthContext';
import { RequireAuth } from '../src/auth/RequireAuth';
import { jsonResponse } from './helpers';

function app() {
  return (
    <AuthProvider>
      <MemoryRouter initialEntries={['/pipeline']}>
        <Routes>
          <Route path="/login" element={<div>login page</div>} />
          <Route path="/pipeline" element={<RequireAuth><div>secret</div></RequireAuth>} />
        </Routes>
      </MemoryRouter>
    </AuthProvider>
  );
}

beforeEach(() => localStorage.clear());
afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

describe('F01 RequireAuth', () => {
  it('F01 redirects to login and never renders the child when there is no token', async () => {
    const fetchSpy = vi.fn();
    vi.stubGlobal('fetch', fetchSpy);
    render(app());
    expect(await screen.findByText('login page')).toBeTruthy();
    expect(screen.queryByText('secret')).toBeNull();
    expect(fetchSpy).not.toHaveBeenCalled(); // /api/me is never called
  });

  it('F01 shows neither the child nor a redirect while /api/me is pending', async () => {
    localStorage.setItem('dream_token', 'test-token');
    let release!: (r: Response) => void;
    vi.stubGlobal('fetch', vi.fn(() => new Promise<Response>((res) => { release = res; })));
    render(app());
    expect(screen.queryByText('secret')).toBeNull();
    expect(screen.queryByText('login page')).toBeNull();
    await act(async () => release(jsonResponse({ email: 'a@example.test', name: null, picture: null })));
    expect(await screen.findByText('secret')).toBeTruthy();
  });
});
