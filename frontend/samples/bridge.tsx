import { useState } from 'react';
import { createRoot } from 'react-dom/client';
import { DealWorkspaceFixture } from '../src/components/DealWorkspaceFixture';
import { bridgeFixtureView, BRIDGE_APP_JOB_STATES } from '../src/lib/bridgeFixtureView';
import '../src/index.css';

function Sample() {
  const [state, setState] = useState('awaiting_cp1');
  const [fault, setFault] = useState('none');
  const now = Date.now();
  const snapshot = {
    schema_version: 1,
    identity: { state: fault === 'denied' ? 'denied' : 'verified', principal_id: 'fixture-principal',
      twenty_user_id: 'fixture-user', email: 'analyst@example.invalid', email_verified: true,
      twenty_workspace_id: fault === 'workspace' ? 'foreign' : 'fixture-workspace', roles: ['fixture-reader'],
      expires_at: new Date(now + (fault === 'expired' ? -60000 : 3600000)).toISOString() },
    link: { state: 'active', link_id: 'fixture-link', app_deal_id: 'fixture-deal',
      twenty_workspace_id: 'fixture-workspace', twenty_opportunity_id: 'fixture-opportunity' },
    status: { source: 'dream_app', app_deal_id: 'fixture-deal', link_id: 'fixture-link', job_state: state,
      stale: fault === 'stale', gates: { state: fault === 'red' ? 'red' : 'unknown' } },
    conversation: fault === 'hermes' ? null : { state: 'open', conversation_id: 'fixture-conversation',
      app_deal_id: 'fixture-deal', link_id: 'fixture-link', principal_id: 'fixture-principal' },
  };
  return <main style={{maxWidth:800,margin:'auto',padding:32,color:'#1e293b',background:'#fff'}}>
    <h1 className="text-2xl">Read-only bridge fixture</h1>
    <p>This proposal has no real identity, CRM or Hermes transport. Its metrics and claims are never projected.</p>
    <label>App status <select value={state} onChange={e=>setState(e.target.value)}>
      {BRIDGE_APP_JOB_STATES.map(s=><option key={s}>{s}</option>)}
    </select></label>{' '}
    <label>Fixture condition <select value={fault} onChange={e=>setFault(e.target.value)}>
      {['none','denied','expired','workspace','stale','red','hermes'].map(s=><option key={s}>{s}</option>)}
    </select></label>
    <DealWorkspaceFixture view={bridgeFixtureView(snapshot,'fixture-workspace','fixture-opportunity',now)} />
    <a href="/__demo__/">Back to sample instructions</a>
  </main>;
}
createRoot(document.getElementById('root')!).render(<Sample />);
