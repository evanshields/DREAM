// F02 401 clears the token, F03 ApiError carries the server detail.
import { describe, it, expect, vi, afterEach, beforeEach } from 'vitest';
import { render, screen, cleanup } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from '../src/auth/AuthContext';
import { RequireAuth } from '../src/auth/RequireAuth';
import {
  ApiError,
  getAuthToken,
  setAuthToken,
  setUnauthorizedHandler,
  getJob,
} from '../src/lib/api';
import { jsonResponse } from './helpers';

beforeEach(() => localStorage.clear());
afterEach(() => {
  cleanup();
  setUnauthorizedHandler(null);
  vi.unstubAllGlobals();
});

describe('F02 401 clears the token', () => {
  it('F02 a 401 from the API fires the handler once and rejects with an expired message', async () => {
    setAuthToken('test-token');
    vi.stubGlobal('fetch', vi.fn(async () => jsonResponse({ detail: 'expired' }, 401)));
    const handler = vi.fn(() => setAuthToken(null));
    setUnauthorizedHandler(handler);
    await expect(getJob('job-1')).rejects.toMatchObject({ status: 401, message: expect.stringMatching(/expired/i) });
    expect(handler).toHaveBeenCalledTimes(1);
    expect(getAuthToken()).toBeNull();
  });

  it('F02 a stored token that /api/me rejects with 401 is cleared and the child never renders', async () => {
    setAuthToken('test-token');
    vi.stubGlobal('fetch', vi.fn(async () => jsonResponse({ detail: 'expired' }, 401)));
    render(
      <AuthProvider>
        <MemoryRouter initialEntries={['/pipeline']}>
          <Routes>
            <Route path="/login" element={<div>login page</div>} />
            <Route path="/pipeline" element={<RequireAuth><div>secret</div></RequireAuth>} />
          </Routes>
        </MemoryRouter>
      </AuthProvider>,
    );
    expect(await screen.findByText('login page')).toBeTruthy();
    expect(screen.queryByText('secret')).toBeNull();
    expect(getAuthToken()).toBeNull();
  });
});

describe('F03 ApiError carries the server detail', () => {
  it('F03 422 detail becomes the error message and status', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => jsonResponse({ detail: 'exit cap must be positive' }, 422)));
    const err = await getJob('job-1').catch((e) => e);
    expect(err).toBeInstanceOf(ApiError);
    expect(err.status).toBe(422);
    expect(err.message).toBe('exit cap must be positive');
  });

  it('F03 a non-JSON 500 body gives a generic message, never undefined', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => new Response('<html>boom</html>', { status: 500, statusText: 'Server Error' })));
    const err = await getJob('job-1').catch((e) => e);
    expect(err).toBeInstanceOf(ApiError);
    expect(err.status).toBe(500);
    expect(err.message).toMatch(/500/);
    expect(err.message).not.toMatch(/undefined/);
  });
});
