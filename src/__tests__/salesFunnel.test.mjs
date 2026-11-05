import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { contactHref, planPrice, scrollToSection } from '../lib/salesFunnel.ts';

const page = readFileSync(new URL('../pages/SalesFunnel.tsx', import.meta.url), 'utf8');

// Return the opening tag text of every <button ...> in the page (handles > inside {...}).
function buttonTags(source) {
  const tags = [];
  let from = 0;
  while ((from = source.indexOf('<button', from)) !== -1) {
    let depth = 0;
    let end = from;
    for (; end < source.length; end++) {
      const ch = source[end];
      if (ch === '{') depth++;
      else if (ch === '}') depth--;
      else if (ch === '>' && depth === 0) break;
    }
    tags.push(source.slice(from, end + 1));
    from = end + 1;
  }
  return tags;
}

test('billing toggle prices: annual and monthly, about 20 percent apart', () => {
  assert.equal(planPrice('starter', 'annual'), 199);
  assert.equal(planPrice('starter', 'monthly'), 249);
  assert.equal(planPrice('professional', 'annual'), 499);
  assert.equal(planPrice('professional', 'monthly'), 625);
  for (const plan of ['starter', 'professional']) {
    const saved = 1 - planPrice(plan, 'annual') / planPrice(plan, 'monthly');
    assert.ok(Math.abs(saved - 0.2) < 0.005, `${plan} saves ${saved}`);
  }
});

test('scrollToSection scrolls smoothly and never touches the location hash', () => {
  const calls = [];
  const doc = {
    getElementById: (id) => (id === 'pricing' ? { scrollIntoView: (o) => calls.push(o) } : null),
  };
  assert.equal(scrollToSection('pricing', doc), true);
  assert.deepEqual(calls, [{ behavior: 'smooth' }]);
  assert.equal(scrollToSection('missing', doc), false);
  assert.equal(calls.length, 1);
});

test('contactHref only builds a mailto from a valid configured address', () => {
  assert.equal(contactHref(undefined, 'Hi'), null);
  assert.equal(contactHref('', 'Hi'), null);
  assert.equal(contactHref('not an email', 'Hi'), null);
  assert.equal(contactHref('a@b.co?bcc=x@y.co', 'Hi'), null);
  assert.equal(contactHref(' sales@example.com ', 'Demo request'), 'mailto:sales@example.com?subject=Demo%20request');
});

test('the page has no href="#..." anchors that would rewrite the hash router', () => {
  assert.deepEqual(page.match(/href="#[^"]*"/g) ?? [], []);
});

test('every section the nav scrolls to exists', () => {
  for (const id of ['features', 'how-it-works', 'pricing', 'testimonials']) {
    assert.match(page, new RegExp(`id="${id}"`), id);
    assert.match(page, new RegExp(`scrollToSection\\('${id}'\\)`), id);
  }
});

test('no dead buttons: every button has a click handler or is explicitly disabled', () => {
  const dead = buttonTags(page).filter((tag) => !/onClick=/.test(tag) && !/\bdisabled\b/.test(tag));
  assert.deepEqual(dead, []);
});

test('Sign In is wired and Contact Sales no longer opens the demo dashboard', () => {
  assert.match(page, /onClick=\{onGetStarted\}[^>]*>\s*Sign In/);
  assert.doesNotMatch(page, /Watch Demo/);
  // The Enterprise card must not bind its "Contact Sales" label to onGetStarted.
  assert.match(page, /ctaAction: 'contact'/);
  assert.match(page, /contactHref\(/);
});

test('no real third-party firm names or unsupported security claims are presented as proof', () => {
  for (const name of ['Blackstone', 'Starwood', 'Greystar', 'Brookfield', 'CBRE']) {
    assert.doesNotMatch(page, new RegExp(name), name);
  }
  assert.doesNotMatch(page, /bank-level encryption/i);
  assert.doesNotMatch(page, /Trusted by leading/i);
  // Sample figures and quotes must be labelled as samples.
  assert.match(page, /SAMPLE_CONTENT_NOTICE/);
});
