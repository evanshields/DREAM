import test from 'node:test';
import assert from 'node:assert/strict';
import React from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { MonoResultView } from '../src/components/mono/MonoResults';
import { monoValue } from '../src/components/mono/MonoEvidence';
import type { MonoResult } from '../src/lib/monoApi';

const result = (checks: unknown, value: unknown = 123, metadata: unknown = {
  unit: 'USD', applicability: { status: 'applies' }, availability: { status: 'available' },
}) => ({ result_id: 'synthetic', outputs: { out_noi_y1: value }, output_metadata: { out_noi_y1: metadata },
  checks, artifact_sha256: 'synthetic', identity: {} }) as MonoResult;

test('unverified native output is withheld in current and historical panels', () => {
  for (const checks of [{}, { release_passed: false }, { release_passed: 1 }]) {
    for (const historical of [false, true]) {
      const html = renderToStaticMarkup(<MonoResultView result={result(checks)} historical={historical} />);
      assert.ok(!html.includes('$123.00'));
      assert.ok(!html.includes('Validated current result'));
    }
  }
});

test('output availability and numeric types are checked before formatting', () => {
  for (const metadata of [{}, { unit: 'USD', availability: { status: 'blocked' } },
    { unit: 'USD', availability: { status: 'available' }, applicability: { status: 'unresolved' } }]) {
    const html = renderToStaticMarkup(<MonoResultView result={result({ release_passed: true }, 123, metadata)} />);
    assert.ok(!html.includes('$123.00'));
    assert.ok(html.includes('Unavailable'));
  }
  for (const value of [null, undefined, NaN, Infinity, '123']) {
    const sample = result({ release_passed: true });
    sample.outputs.out_noi_y1 = value;
    const html = renderToStaticMarkup(<MonoResultView result={sample} />);
    assert.ok(html.includes('Unavailable'));
  }
  assert.match(renderToStaticMarkup(<MonoResultView result={result({ release_passed: true }, 0)} />), /\$0\.00/);
});

test('unsafe browser integers use exact server text or stay unavailable', () => {
  assert.equal(monoValue(9007199254740992, 'count', '9007199254740993'), '9,007,199,254,740,993');
  assert.equal(monoValue(9007199254740992, 'count'), 'Unavailable');
});
