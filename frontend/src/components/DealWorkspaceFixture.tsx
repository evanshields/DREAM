import type { BridgeFixtureView } from '../lib/bridgeFixtureView';

// Deliberately unmounted: review against local DTOs before any production wiring.
export function DealWorkspaceFixture({ view }: { view: BridgeFixtureView }) {
  return <section aria-label="Local Deal workspace fixture" className="space-y-4 rounded-xl border border-slate-700 p-6">
    <p className="text-sm text-amber-300">Local fixture preview</p>
    <h2 className="text-xl font-semibold">Deal workspace</h2>
    <p role="status">{view.reason}</p>
    {view.state === 'ready' && <dl className="grid gap-3 sm:grid-cols-2">
      <div><dt>Current user</dt><dd className="break-all">{view.userLabel}</dd></div>
      <div><dt>Opportunity</dt><dd className="break-all">{view.opportunityId}</dd></div>
      <div><dt>DREAM deal</dt><dd className="break-all">{view.dealId}</dd></div>
      <div><dt>Underwriting status</dt><dd>{view.statusLabel}</dd></div>
      <div><dt>Gate evidence</dt><dd>{view.gateLabel}</dd></div>
      <div className="sm:col-span-2"><dt>Conversation</dt><dd>{view.conversationLabel}</dd></div>
    </dl>}
  </section>;
}
