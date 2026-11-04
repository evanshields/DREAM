// Gap map F25: the display formatters must show a dash for a missing or non-finite number,
// never "NaN%" or "$NaN". Synthetic values only. Run: node --test frontend/tests/format.test.ts
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { fmtUSD, fmtUSDFull, fmtPct, fmtPct1, fmtEM } from '../src/lib/format.ts';

const BAD: Array<[string, unknown]> = [
  ['NaN', NaN],
  ['Infinity', Infinity],
  ['-Infinity', -Infinity],
  ['null', null],
  ['undefined', undefined],
];
const FORMATTERS: Array<[string, (v: number) => string]> = [
  ['fmtUSD', fmtUSD],
  ['fmtUSDFull', fmtUSDFull],
  ['fmtPct', fmtPct],
  ['fmtPct1', fmtPct1],
  ['fmtEM', fmtEM],
];

for (const [fname, fn] of FORMATTERS) {
  for (const [label, bad] of BAD) {
    test(`${fname}(${label}) shows a dash, not a made-up number`, () => {
      assert.equal(fn(bad as number), '—');
    });
  }
}

test('control: finite values still format as before', () => {
  assert.equal(fmtPct(0.2251), '22.51%');
  assert.equal(fmtPct1(0.2251), '22.5%');
  assert.equal(fmtEM(1.5), '1.50x');
  assert.equal(fmtUSD(2_500_000), '$2.50M');
  assert.equal(fmtUSD(1234), '$1,234');
  assert.equal(fmtUSDFull(1234), '$1,234');
});

test('control: a verified zero stays zero', () => {
  assert.equal(fmtPct(0), '0.00%');
  assert.equal(fmtEM(0), '0.00x');
  assert.equal(fmtUSD(0), '$0');
});
