import test from 'node:test';
import assert from 'node:assert/strict';
import { bridgeFixtureView } from '../src/lib/bridgeFixtureView.ts';

const now = Date.parse('2026-10-04T04:00:00Z');
const snapshot = () => ({
  schema_version: 1,
  identity: { state: 'verified', principal_id: 'fixture-principal', twenty_user_id: 'fixture-user', email: 'analyst@example.invalid',
    email_verified: true, twenty_workspace_id: 'fixture-workspace', roles: ['fixture-reader'], expires_at: '2026-10-04T05:00:00Z' },
  link: { state: 'active', link_id: 'fixture-link', app_deal_id: 'fixture-deal',
    twenty_workspace_id: 'fixture-workspace', twenty_opportunity_id: 'fixture-opportunity' },
  status: { source: 'dream_app', app_deal_id: 'fixture-deal', link_id: 'fixture-link', job_state: 'analyzing', stale: false },
  conversation: { state: 'open', conversation_id: 'fixture-conversation', app_deal_id: 'fixture-deal',
    link_id: 'fixture-link', principal_id: 'fixture-principal' },
});
const view = value => bridgeFixtureView(value, 'fixture-workspace', 'fixture-opportunity', now);

test('verified local fixture shows identity, exact link and read-only app status', () => {
  const result = view(snapshot());
  assert.equal(result.state, 'ready');
  assert.equal(result.dealId, 'fixture-deal');
  assert.equal(result.statusLabel, 'Analyzing');
  assert.match(result.reason, /Local fixture only/);
});

test('denied, unavailable, expired, malformed and cross-workspace identity fail closed', () => {
  for (const identity of [null, {state:'denied'}, {state:'unavailable'},
    {...snapshot().identity, expires_at:'2026-10-04T03:59:59Z'},
    {...snapshot().identity, twenty_workspace_id:'other'},
    {...snapshot().identity, email_verified:false}, {...snapshot().identity, roles:[]}]) {
    assert.deepEqual(Object.keys(view({...snapshot(), identity})).sort(), ['reason','state']);
    assert.equal(view({...snapshot(), identity}).state, 'blocked');
  }
});

test('link mismatch, repair, archive and absence expose no deal data', () => {
  for (const link of [null, {...snapshot().link,state:'repair_required'}, {...snapshot().link,state:'archived'},
    {...snapshot().link,twenty_opportunity_id:'other'}, {...snapshot().link,twenty_workspace_id:'other'}]) {
    assert.equal(view({...snapshot(),link}).state,'blocked');
    assert.equal(view({...snapshot(),link}).dealId,undefined);
  }
});

test('C2 vocabulary and foreign app-deal status are never translated to CP1', () => {
  for (const job_state of ['waiting_for_evan', 'resumed', 'skipped', 'unknown_state', 'future_state', 'toString']) {
    assert.equal(view({...snapshot(),status:{...snapshot().status,job_state}}).state,'blocked');
  }
  assert.equal(view({...snapshot(),status:{...snapshot().status,app_deal_id:'foreign'}}).state,'blocked');
  assert.equal(view({...snapshot(),status:{...snapshot().status,source:'c2',job_state:'done'}}).state,'blocked');
});

test('CP1 remains a human stop and done does not assert approval', () => {
  assert.equal(view({...snapshot(),status:{...snapshot().status,job_state:'awaiting_cp1'}}).statusLabel,'Awaiting human review');
  assert.match(view({...snapshot(),status:{...snapshot().status,job_state:'done'}}).statusLabel,/approval is separate/);
});

test('stale values, narrative claims, metrics and secret-like fields are never projected', () => {
  const fixture = snapshot();
  fixture.status = {...fixture.status, stale:true, gates:{state:'red'}, metrics:{items:[{irr:0.9}]}};
  fixture.conversation.content = 'Claim: IRR 90 percent';
  fixture.service_token = 'FIXTURE_ONLY_DO_NOT_RENDER';
  const result = view(fixture);
  assert.match(result.statusLabel,/stale/);
  assert.match(result.gateLabel,/stale/);
  assert.match(view({...fixture,status:{...fixture.status,stale:false}}).gateLabel,/RED gate/);
  assert.match(view({...fixture,status:{...fixture.status,stale:false,gates:{state:'green'}}}).gateLabel,/unavailable/);
  const rendered = JSON.stringify(result);
  for(const forbidden of ['0.9','90 percent','FIXTURE_ONLY_DO_NOT_RENDER','service_token','metrics']) assert.ok(!rendered.includes(forbidden));
});

test('Hermes loss or foreign conversation preserves read-only DREAM status', () => {
  for(const conversation of [null,{state:'unavailable'}, {...snapshot().conversation,app_deal_id:'foreign'},
    {...snapshot().conversation,principal_id:'foreign'}, {...snapshot().conversation,state:'future_state'}]) {
    const result = view({...snapshot(),conversation});
    assert.equal(result.state,'ready');
    assert.equal(result.statusLabel,'Analyzing');
    assert.equal(result.conversationLabel,'Hermes conversation unavailable');
  }
});

test('missing version, unknown version and malformed snapshots fail closed', () => {
  for(const malformed of [null, [], {}, {...snapshot(),schema_version:2}, {...snapshot(),status:{}}]) assert.equal(view(malformed).state,'blocked');
});

test('matching empty context IDs cannot produce a ready view', () => {
  for(const empty of ['', '   ']) {
    const fixture = snapshot();
    fixture.identity.twenty_workspace_id = empty;
    fixture.link.twenty_workspace_id = empty;
    fixture.link.twenty_opportunity_id = empty;
    assert.equal(bridgeFixtureView(fixture, empty, empty, now).state,'blocked');
  }
});
