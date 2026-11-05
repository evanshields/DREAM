import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { DEFAULT_VIEW, VIEWS, viewFromHash } from '../lib/routing.ts';

test('an empty hash has no view and the default view is the landing page', () => {
  assert.equal(viewFromHash(''), null);
  assert.equal(viewFromHash('#'), null);
  assert.equal(DEFAULT_VIEW, 'landing');
});

test('every real view resolves from its hash', () => {
  for (const view of VIEWS) {
    assert.equal(viewFromHash(`#${view}`), view);
    assert.equal(viewFromHash(view), view);
  }
});

test('in-page anchors and unknown hashes never resolve to a view', () => {
  for (const hash of ['#features', '#how-it-works', '#pricing', '#testimonials', '#nope', '#Dashboard']) {
    assert.equal(viewFromHash(hash), null, hash);
  }
});

test('App.tsx routes through viewFromHash and the default view', () => {
  const app = readFileSync(new URL('../App.tsx', import.meta.url), 'utf8');
  assert.match(app, /viewFromHash\(window\.location\.hash\)/);
  assert.match(app, /window\.location\.hash = DEFAULT_VIEW/);
  assert.match(app, /if \(!viewFromHash\(window\.location\.hash\)\)/);
  assert.match(app, /useState<ViewState>\(DEFAULT_VIEW\)/);
  assert.match(app, /onGetStarted=\{\(\) => navigate\('dashboard'\)\}/);
});

test('Layout removes the dark class when it unmounts', () => {
  const layout = readFileSync(new URL('../components/Layout.tsx', import.meta.url), 'utf8');
  assert.match(layout, /return \(\) => document\.documentElement\.classList\.remove\('dark'\)/);
});
