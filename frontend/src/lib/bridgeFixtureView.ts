// Local fixture consumer for the Claude-authored proposal. No HTTP or auth adapter.
export interface BridgeFixtureView {
  state: 'blocked' | 'ready';
  reason: string;
  opportunityId?: string;
  dealId?: string;
  userLabel?: string;
  statusLabel?: string;
  gateLabel?: string;
  conversationLabel?: string;
}

type RecordValue = Record<string, unknown>;
const record = (value: unknown): RecordValue | undefined =>
  value !== null && typeof value === 'object' && !Array.isArray(value) ? value as RecordValue : undefined;
const text = (value: unknown): value is string => typeof value === 'string' && value.trim().length > 0;
const blocked = (reason: string): BridgeFixtureView => ({ state: 'blocked', reason });
const labels: Record<string, string> = {
  queued: 'Queued', needs_routing: 'Routing required', awaiting_input: 'Input required',
  analyzing: 'Analyzing', computing: 'Computing', awaiting_cp1: 'Awaiting human review',
  done: 'Run reported complete; approval is separate', failed: 'Run failed', cancelled: 'Run cancelled',
};

export function bridgeFixtureView(
  value: unknown, workspaceId: string, opportunityId: string, nowMs: number,
): BridgeFixtureView {
  const snapshot = record(value);
  if (!snapshot || snapshot.schema_version !== 1 || !Number.isFinite(nowMs) ||
      !text(workspaceId) || !text(opportunityId)) return blocked('Malformed fixture');
  const identity = record(snapshot.identity);
  if (!identity || identity.state !== 'verified') return blocked('Identity unavailable or denied');
  if (!text(identity.principal_id) || !text(identity.twenty_user_id) || !text(identity.email) || identity.email_verified !== true ||
      identity.twenty_workspace_id !== workspaceId || !text(identity.expires_at) ||
      !Number.isFinite(Date.parse(identity.expires_at)) || Date.parse(identity.expires_at) <= nowMs ||
      !Array.isArray(identity.roles) || identity.roles.length === 0 || !identity.roles.every(text)) {
    return blocked('Identity malformed, expired or outside this workspace');
  }
  const link = record(snapshot.link);
  if (!link || link.state !== 'active') return blocked('Deal link unavailable, archived or needs repair');
  if (!text(link.link_id) || !text(link.app_deal_id) || link.twenty_workspace_id !== workspaceId ||
      link.twenty_opportunity_id !== opportunityId) return blocked('Deal link context does not match');
  const status = record(snapshot.status);
  if (!status || status.source !== 'dream_app' || status.app_deal_id !== link.app_deal_id || status.link_id !== link.link_id ||
      !text(status.job_state) || !Object.hasOwn(labels, status.job_state) || typeof status.stale !== 'boolean') {
    return blocked('DREAM status unavailable, malformed or uses an unknown state');
  }
  const conversation = record(snapshot.conversation);
  const gates = record(status.gates);
  const gateLabel = status.stale ? 'Gate proof stale; results unavailable' :
    gates?.state === 'red' ? 'RED gate; outputs blocked' :
    gates?.state === 'amber' ? 'Gate warning; review required' :
    gates?.state === 'green' && text(gates.receipt_ref) ? 'Fixture gate receipt provided' :
    'Gate proof unavailable; results unavailable';
  const matchingConversation = conversation && conversation.app_deal_id === link.app_deal_id &&
    conversation.link_id === link.link_id && conversation.principal_id === identity.principal_id &&
    text(conversation.conversation_id);
  let conversationLabel = 'Hermes conversation unavailable';
  if (matchingConversation && conversation.state === 'open') conversationLabel = 'Local conversation fixture; claims are unverified';
  else if (matchingConversation && conversation.state === 'closed') conversationLabel = 'Conversation closed';
  // A projection whitelist intentionally omits all metrics, message content and unknown
  // fields. The first-slice plan excludes metrics; claims can never become headlines.
  return {
    state: 'ready', reason: 'Local fixture only; live identity and transport are not connected',
    opportunityId, dealId: link.app_deal_id, userLabel: identity.email,
    statusLabel: status.stale ? 'Status stale; refresh required' : labels[status.job_state],
    gateLabel,
    conversationLabel,
  };
}
