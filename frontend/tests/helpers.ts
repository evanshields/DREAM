// Shared synthetic helpers for the slice 2 tests. No live service, no real token.
import { vi } from 'vitest';

export function jsonResponse(body: unknown, status = 200, headers: Record<string, string> = {}): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json', ...headers },
  });
}

// Stub globalThis.fetch with a router: [matcher, handler] pairs, first match wins.
export function stubFetch(routes: Array<[RegExp, (url: string, init?: RequestInit) => Response | Promise<Response>]>) {
  const fn = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
    const url = String(input);
    for (const [re, handler] of routes) if (re.test(`${init?.method ?? 'GET'} ${url}`)) return handler(url, init);
    return jsonResponse({ detail: `unmocked ${url}` }, 404);
  });
  vi.stubGlobal('fetch', fn);
  return fn;
}
