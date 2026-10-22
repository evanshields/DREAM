import { ApiError, apiRequest } from './api';

export type MonoScalar = string | number | boolean | null;
export type MonoRecord = Record<string, unknown>;

export interface MonoIdentity {
  deal_sha256: string;
  bundle_sha256: string;
  map_sha256: string;
  template_sha256: string;
  code_sha256: string;
  ledger_sha256: string | null;
  source_hashes: Record<string, string>;
}

export interface MonoAssumption {
  id: string;
  group: string;
  label: string;
  value: MonoScalar;
  edit_value?: string;
  unit: string;
  bucket: string;
  source: MonoRecord | null;
  applicability: unknown;
  verified_applicability: { status: string; rule_id?: string | null; reason?: string; evidence?: unknown };
  missing_reasons: string[];
  history: unknown[];
}

export interface MonoResult {
  result_id: string;
  outputs: Record<string, unknown>;
  output_metadata: Record<string, MonoRecord>;
  checks: unknown;
  artifact_sha256: string;
  identity: MonoIdentity;
  historical_profile?: MonoRecord | null;
  selected_financial_projection?: {
    provider_id: string;
    historical_profile: MonoRecord | null;
    metrics: Record<string, {semantic_id: string; value: unknown; unit: string; period: unknown;
      availability: string; binding_locator: unknown}>;
    projection_sha256: string;
  } | null;
}

export interface MonoJob {
  job_id: string;
  deal_id: string;
  revision: number;
  state: string;
  created_at: string;
  updated_at: string;
  elapsed_seconds: number;
  identity: MonoIdentity;
  diagnostics: unknown[];
  warnings: unknown[];
  result: MonoResult | null;
  is_current: boolean;
}

export interface MonoView {
  contract_version: number;
  deal_id: string;
  name: string;
  revision: number;
  identity: MonoIdentity;
  assumptions: MonoAssumption[];
  readiness: {
    ready: boolean;
    recorded_d_count: number;
    unverified_field_count: number;
    diagnostic_count: number;
    problems: unknown[];
  };
  gates: { comps: MonoRecord | null; go_no_go: MonoRecord | null; status: string };
  current_result: MonoResult | null;
  jobs: MonoJob[];
  narrative: { status: string; provider: string; revision: number; text: string; references: unknown[]; [key: string]: unknown };
  can_edit: boolean;
  operation?: { kind: string; event: MonoRecord; applied_revision: number; current_revision: number; replayed: boolean };
}

export interface MonoRevisionRequest {
  expected_revision: number;
  expected_deal_sha256: string;
}

export interface MonoEditRequest extends MonoRevisionRequest {
  field_id: string;
  entered_value: MonoScalar;
  unit: string;
  reason: string;
  idempotency_key: string;
}

export interface MonoCalculateRequest extends MonoRevisionRequest {
  idempotency_key: string;
}

export interface MonoGateRequest extends MonoRevisionRequest {
  gate: 'comps' | 'go_no_go';
  decision: 'confirm' | 'go' | 'no_go';
  reason: string;
  idempotency_key: string;
  comps_sha256?: string;
  result_id?: string;
}

const root = (dealId: string) => `/deals/${encodeURIComponent(dealId)}/mono`;
export const getMonoDeal = (dealId: string, signal?: AbortSignal) =>
  apiRequest<MonoView>(root(dealId), { signal });
export const editMonoAssumption = (dealId: string, body: MonoEditRequest, signal?: AbortSignal) =>
  apiRequest<MonoView>(`${root(dealId)}/edits`, { method: 'POST', body, signal });
export const calculateMono = (dealId: string, body: MonoCalculateRequest, signal?: AbortSignal) =>
  apiRequest<MonoJob>(`${root(dealId)}/calculations`, { method: 'POST', body, signal });
export const getMonoJob = (dealId: string, jobId: string, signal?: AbortSignal) =>
  apiRequest<MonoJob>(`${root(dealId)}/jobs/${encodeURIComponent(jobId)}`, { signal });
export const cancelMonoJob = (dealId: string, jobId: string, signal?: AbortSignal) =>
  apiRequest<MonoJob>(`${root(dealId)}/jobs/${encodeURIComponent(jobId)}/cancel`, { method: 'POST', signal });
export const recordMonoGate = (dealId: string, body: MonoGateRequest, signal?: AbortSignal) =>
  apiRequest<MonoView>(`${root(dealId)}/gates`, { method: 'POST', body, signal });

export interface MonoPublicationJob {
  job_id: string;
  deal_id: string;
  revision: number;
  state: string;
  created_at: string;
  updated_at: string;
  elapsed_seconds: number;
  diagnostics: unknown[];
  steps: string[];
  is_current: boolean;
  cancel_requested?: boolean;
}

export interface MonoPublications {
  deal_id: string;
  revision: number;
  can_publish: boolean;
  blocking_reasons: string[];
  warnings: string[];
  current: MonoPublicationJob | null;
  jobs: MonoPublicationJob[];
  external_distribution_authorized: boolean;
}

const publications = (dealId: string) => `${root(dealId)}/publications`;
export const getMonoPublications = (dealId: string, signal?: AbortSignal) =>
  apiRequest<MonoPublications>(publications(dealId), { signal });
export const publishMono = (dealId: string, body: MonoCalculateRequest) =>
  apiRequest<MonoPublicationJob>(publications(dealId), { method: 'POST', body });
export const cancelMonoPublication = (dealId: string, jobId: string) =>
  apiRequest<MonoPublicationJob>(`${publications(dealId)}/${encodeURIComponent(jobId)}/cancel`, { method: 'POST', body: {} });
export type MonoDeliverable = 'package' | 'memo' | 'onepager' | 'deck' | 'workbook';
export type MonoDownloadFormat = 'archive' | 'pdf' | 'editable' | 'workbook';
export const downloadMonoPublication = (dealId: string, jobId: string, kind: MonoDeliverable, format: MonoDownloadFormat) =>
  apiRequest<Blob>(`${publications(dealId)}/${encodeURIComponent(jobId)}/downloads/${kind}/${format}`, { responseType: 'blob' });

export const revisionOf = (view: MonoView): MonoRevisionRequest => ({
  expected_revision: view.revision,
  expected_deal_sha256: view.identity.deal_sha256,
});

export function monoConflict(error: unknown): { message: string; current_revision?: number } | null {
  if (!(error instanceof ApiError) || error.status !== 409) return null;
  try {
    const detail: unknown = JSON.parse(error.message);
    if (detail && typeof detail === 'object') {
      const record = detail as MonoRecord;
      return {
        message: typeof record.message === 'string' ? record.message : 'The deal changed. Reread before resubmitting.',
        current_revision: typeof record.current_revision === 'number' ? record.current_revision : undefined,
      };
    }
  } catch { /* A non-JSON conflict is still a conflict and must never trigger an automatic retry. */ }
  return { message: error.message };
}

export const monoError = (error: unknown) => error instanceof Error ? error.message : 'The request could not be completed.';
