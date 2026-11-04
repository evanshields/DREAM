// Synthetic fixtures only. Run with: npm test (bundles with esbuild, runs node:test).
import test from 'node:test';
import assert from 'node:assert/strict';
import { getUwSnapshot, parseUwSnapshotView } from '../src/lib/uwSnapshotApi';
import { setUnauthorizedHandler } from '../src/lib/api';

const good = () => ({
  deal_id: 'syn-1',
  state: 'ready',
  blank_reason: null,
  read_only: true,
  snapshot: {
    property_name: 'Fakeville Gardens (synthetic)',
    verdict: 'PASS WITH CONDITIONS: synthetic example only',
    engine_version: 'synthetic-engine-0.0.1',
    unit_mix: [{ unit_type: 'Studio', units: 12, safe_harbor_rent: 1050, in_place_rent: 1075 }],
    seller_t12: [{ line: 'Gross potential rent', amount: 1250000 }],
    seller_t12_noi: 575500,
    stabilized_gpr: 1198800,
    stabilized_noi: 541234,
    exempt_dscr: 1.37,
  },
});

test('well formed view passes through unchanged', () => {
  const r = parseUwSnapshotView(good());
  assert.equal(r.ok, true);
  if (r.ok) assert.deepEqual(r.view, good());
});

test('object engine_version is rejected before render', () => {
  const v = good() as any;
  v.snapshot.engine_version = { major: 1 };
  const r = parseUwSnapshotView(v);
  assert.equal(r.ok, false);
});

test('object engine_version on a blank view is blanked, not rendered', () => {
  const v = good() as any;
  v.state = 'blank';
  v.blank_reason = 'x';
  v.snapshot = { verdict: 'INCOMPLETE', engine_version: { a: 1 } };
  const r = parseUwSnapshotView(v);
  assert.equal(r.ok, false);
});

test('unit_mix that is an object is rejected', () => {
  const v = good() as any;
  v.snapshot.unit_mix = { 0: { unit_type: 'Studio' } };
  assert.equal(parseUwSnapshotView(v).ok, false);
});

test('seller_t12 that is an object is rejected', () => {
  const v = good() as any;
  v.snapshot.seller_t12 = { line: 'x' };
  assert.equal(parseUwSnapshotView(v).ok, false);
});

test('null row in a collection is rejected', () => {
  const v = good() as any;
  v.snapshot.unit_mix = [null];
  assert.equal(parseUwSnapshotView(v).ok, false);
  const w = good() as any;
  w.snapshot.seller_t12 = [null];
  assert.equal(parseUwSnapshotView(w).ok, false);
});

test('object cell inside a row is rejected', () => {
  const v = good() as any;
  v.snapshot.unit_mix = [{ unit_type: 'Studio', units: { n: 1 } }];
  assert.equal(parseUwSnapshotView(v).ok, false);
});

test('non-object view and bad state are rejected', () => {
  assert.equal(parseUwSnapshotView(null).ok, false);
  assert.equal(parseUwSnapshotView([]).ok, false);
  const v = good() as any;
  v.state = 'weird';
  assert.equal(parseUwSnapshotView(v).ok, false);
});

test('absent collections are allowed (treated as empty)', () => {
  const v = good() as any;
  delete v.snapshot.unit_mix;
  delete v.snapshot.seller_t12;
  assert.equal(parseUwSnapshotView(v).ok, true);
});

test('401 invokes the shared unauthorized handler', async () => {
  let called = 0;
  setUnauthorizedHandler(() => { called += 1; });
  const orig = globalThis.fetch;
  globalThis.fetch = (async () => new Response('{}', { status: 401 })) as typeof fetch;
  try {
    await assert.rejects(() => getUwSnapshot('syn-1'), (e: any) => e.status === 401);
    assert.equal(called, 1);
  } finally {
    globalThis.fetch = orig;
    setUnauthorizedHandler(null);
  }
});

test('success goes through shared request and validates', async () => {
  const orig = globalThis.fetch;
  let seen: { url: string; method?: string } | null = null;
  globalThis.fetch = (async (url: string, init?: RequestInit) => {
    seen = { url, method: init?.method };
    return new Response(JSON.stringify(good()), { status: 200 });
  }) as typeof fetch;
  try {
    const v = await getUwSnapshot('syn 1');
    assert.equal(v.state, 'ready');
    assert.equal(seen!.method, 'GET');
    assert.ok(seen!.url.endsWith('/deals/syn%201/uw-snapshot'));
  } finally {
    globalThis.fetch = orig;
  }
});

test('malformed 200 body rejects with a clear message', async () => {
  const orig = globalThis.fetch;
  const v = good() as any;
  v.snapshot.unit_mix = [null];
  globalThis.fetch = (async () => new Response(JSON.stringify(v), { status: 200 })) as typeof fetch;
  try {
    await assert.rejects(() => getUwSnapshot('syn-1'), /not in the expected shape/);
  } finally {
    globalThis.fetch = orig;
  }
});
