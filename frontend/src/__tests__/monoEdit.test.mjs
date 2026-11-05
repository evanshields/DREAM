import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { initialEditKind } from '../lib/monoEdit.ts';

test('a missing value starts on a typeable kind, not Null', () => {
  assert.equal(initialEditKind(null, '$'), 'number');
  assert.equal(initialEditKind(null, '%'), 'number');
  assert.equal(initialEditKind(null, 'rate'), 'number');
  assert.equal(initialEditKind(null, 'count'), 'number');
  assert.equal(initialEditKind(null, undefined), 'number');
  assert.equal(initialEditKind(undefined, '$'), 'number');
  assert.equal(initialEditKind(null, 'text'), 'text');
});

test('existing values keep their own kind', () => {
  assert.equal(initialEditKind(5, '$'), 'number');
  assert.equal(initialEditKind(0, '$'), 'number');
  assert.equal(initialEditKind('abc', 'text'), 'text');
  assert.equal(initialEditKind('', 'text'), 'text');
  assert.equal(initialEditKind(true, ''), 'boolean');
  assert.equal(initialEditKind(false, ''), 'boolean');
});

test('the assumptions row uses the helper and no longer starts a missing field on Null', () => {
  const row = readFileSync(new URL('../components/mono/MonoAssumptions.tsx', import.meta.url), 'utf8');
  assert.match(row, /setKind\(initialEditKind\(field\.value, field\.unit\)\)/);
  assert.doesNotMatch(row, /field\.value === null \? 'null'/);
});
