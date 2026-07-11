// DREAM API client — the single seam over the FastAPI backend (same-origin '/api' behind Caddy).
// Token (Google ID token OR app JWT from /api/auth/login) lives in localStorage and rides every
// call as `Authorization: Bearer <token>`. A 401 anywhere clears the token + bounces to /login
// (the bounce is wired via an onUnauthorized hook the AuthProvider registers).
//
// The recalc/sensitivity types + token helpers mirror gemini_ui/api.ts (already contract-correct);
// auth / me / deals / jobs are added here for the full app.

export const API_BASE: string =
  ((import.meta as { env?: { VITE_API_BASE?: string } })?.env?.VITE_API_BASE)?.replace(/\/$/, '') ||
  '/api';

const TOKEN_KEY = 'dream_token';

export function setAuthToken(token: string | null): void {
  try {
    if (token) localStorage.setItem(TOKEN_KEY, token);
    else localStorage.removeItem(TOKEN_KEY);
  } catch {
    /* storage unavailable (incognito) — calls just go unauthenticated */
  }
}

export function getAuthToken(): string | null {
  try {
    return localStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
}

// Global 401 handler — AuthProvider registers this so any API call that 401s logs out + redirects.
let onUnauthorized: (() => void) | null = null;
export function setUnauthorizedHandler(fn: (() => void) | null): void {
  onUnauthorized = fn;
}

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
    this.name = 'ApiError';
  }
}

async function request<T>(
  path: string,
  opts: { method?: string; body?: unknown; signal?: AbortSignal; auth?: boolean } = {},
): Promise<T> {
  const { method = 'GET', body, signal, auth = true } = opts;
  const token = getAuthToken();
  const headers: Record<string, string> = {};
  if (body !== undefined) headers['Content-Type'] = 'application/json';
  if (auth && token) headers['Authorization'] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
    signal,
  });

  if (res.status === 401) {
    // expired / invalid token anywhere in the app — bounce to login.
    if (onUnauthorized) onUnauthorized();
    throw new ApiError(401, 'Your session has expired. Please sign in again.');
  }

  if (!res.ok) {
    let detail = `${res.status} ${res.statusText}`;
    try {
      const j = await res.json();
      if (j?.detail) detail = typeof j.detail === 'string' ? j.detail : JSON.stringify(j.detail);
    } catch {
      /* non-JSON error body — keep status text */
    }
    throw new ApiError(res.status, detail);
  }

  // 204 / empty
  const text = await res.text();
  return (text ? JSON.parse(text) : undefined) as T;
}

// ===========================================================================
// Auth + identity
// ===========================================================================

export interface LoginResponse {
  access_token: string;
  token_type: string;
  email: string;
}

export interface MeResponse {
  email: string | null;
  name: string | null;
  picture: string | null;
}

export function login(username: string, password: string): Promise<LoginResponse> {
  return request<LoginResponse>('/auth/login', {
    method: 'POST',
    body: { username, password },
    auth: false,
  });
}

export function me(): Promise<MeResponse> {
  return request<MeResponse>('/me');
}

// ===========================================================================
// Deals (pipeline) — GET /api/deals
// ===========================================================================

export interface DealHeadlineMetrics {
  irr?: number;
  equity_multiple?: number;
  coc_stabilized?: number;
  exit_value?: number;
  [k: string]: number | number[] | undefined;
}

export interface DealListItem {
  deal_id: string;
  deal_name: string;
  slug: string;
  routing: string; // ACQ | EFB
  mode: string; // HITL | HOTL
  status: string; // draft | computed | populated | exported | archived | gate_failed
  owner: string;
  version: number;
  created_at: string;
  updated_at: string;
  headline_metrics: DealHeadlineMetrics;
}

export function listDeals(filters?: {
  owner?: string;
  routing?: string;
  status?: string;
}): Promise<DealListItem[]> {
  const q = new URLSearchParams();
  if (filters?.owner) q.set('owner', filters.owner);
  if (filters?.routing) q.set('routing', filters.routing);
  if (filters?.status) q.set('status', filters.status);
  const qs = q.toString();
  return request<DealListItem[]>(`/deals${qs ? `?${qs}` : ''}`);
}

// ===========================================================================
// Jobs (chat-bot underwrite lifecycle)
// ===========================================================================

export type JobStatus =
  | 'submitted'
  | 'routing'
  | 'awaiting_input'
  | 'analyzing'
  | 'synthesizing'
  | 'awaiting_cp1'
  | 'completed'
  | 'failed'
  | 'cancelled';

export interface OpenQuestion {
  id: string;
  field: string;
  question: string;
  current_value: unknown;
  source: 'cited' | 'llm-inferred' | string;
  options?: string[] | null;
  answered: boolean;
  answer: unknown;
}

export interface JobView {
  job_id: string;
  deal_id: string;
  status: JobStatus;
  phase: string;
  routing: string;
  mode: string;
  cancel_requested: boolean;
  error: string | null;
  open_questions: OpenQuestion[];
  blocking_questions: OpenQuestion[];
  // present only at awaiting_cp1:
  spec?: Record<string, unknown>;
  headline_metrics?: DealHeadlineMetrics;
  gate_summary?: Record<string, unknown>;
}

export interface SubmitJobRequest {
  intake_summary: {
    routing: string;
    deal_name: string;
    critical_inputs: Record<string, unknown>;
    [k: string]: unknown;
  };
  deal_docs?: Record<string, unknown>;
  owner: string;
  deal_name: string;
  routing: string;
  idempotency_key?: string;
}

// The underwrite call can take 20s–4min with live Kimi. NO short fetch timeout (PRD §4.3).
export function submitJob(req: SubmitJobRequest, signal?: AbortSignal): Promise<JobView> {
  return request<JobView>('/jobs', { method: 'POST', body: req, signal });
}

export function getJob(jobId: string, signal?: AbortSignal): Promise<JobView> {
  return request<JobView>(`/jobs/${encodeURIComponent(jobId)}`, { signal });
}

export function answerJob(
  jobId: string,
  questionId: string,
  answer: unknown,
  signal?: AbortSignal,
): Promise<JobView> {
  return request<JobView>(`/jobs/${encodeURIComponent(jobId)}/answer`, {
    method: 'POST',
    body: { question_id: questionId, answer },
    signal,
  });
}

export function cancelJob(jobId: string): Promise<JobView> {
  return request<JobView>(`/jobs/${encodeURIComponent(jobId)}/cancel`, { method: 'POST' });
}

// ===========================================================================
// Recalc + sensitivity (assumption dashboard) — mirrors gemini_ui/api.ts exactly
// ===========================================================================

export interface ACQRecalcRequest {
  bridge_loan: number;
  bridge_rate: number;
  bridge_io_years: number;
  refi_loan: number;
  refi_rate: number;
  refi_io_years: number;
  refi_amort_years: number;
  refi_year: number;

  total_equity: number;
  noi_series: number[];
  exit_cap: number;
  sale_year: number;
  costs_of_sale: number;

  servicing_spread: number;
  refi_cost_pct: number;
  exit_on_forward_noi: boolean;

  gpr_series?: number[] | null;
  egi_series?: number[] | null;
  opex_series?: number[] | null;
  vacancy_series?: number[] | null;
  debt_service?: number[] | null;
  years?: number;
}

export interface HeadlineMetrics {
  irr: number;
  equity_multiple: number;
  coc_stabilized: number;
  exit_value: number;
  coc_year1?: number;
  net_sale_proceeds?: number;
  total_equity?: number;
  noi_series?: number[];
  dscr_series?: number[];
  cash_flows?: number[];
  [k: string]: number | number[] | undefined;
}

export interface RecalcResponse {
  headline_metrics: HeadlineMetrics;
}

export type SweepField =
  | 'exit_cap'
  | 'refi_rate'
  | 'bridge_rate'
  | 'servicing_spread'
  | 'costs_of_sale'
  | 'total_equity'
  | 'refi_loan'
  | 'bridge_loan';

export type SweepMetric = 'irr' | 'equity_multiple' | 'coc_stabilized' | 'exit_value';

export interface SensitivityRequest {
  base: ACQRecalcRequest;
  field: SweepField;
  values: number[];
  metric: SweepMetric;
}

export interface SensitivityPoint {
  value: number;
  metric: SweepMetric;
  result: number | null;
}

export interface SensitivityResponse {
  field: SweepField;
  metric: SweepMetric;
  grid: SensitivityPoint[];
}

export function recalc(req: ACQRecalcRequest, signal?: AbortSignal): Promise<RecalcResponse> {
  return request<RecalcResponse>('/recalc', { method: 'POST', body: req, signal });
}

// ===========================================================================
// Bond Screen — EFB bond sizing + companion calculators (all deterministic, no LLM)
// Mirrors backend/routers/recalc.py (EFBUnderwriteRequest / ExitCapRequest /
// AgencySizingRequest) and engine_boundary.py response dicts exactly.
// ===========================================================================

export interface EFBUnderwriteRequest {
  stabilized_noi: number;
  target_dscr: number; // ratio, e.g. 1.15
  bond_rate: number; // decimal, e.g. 0.05
  amortization_years: number;
  annual_property_tax_exempted?: number | null;
  hold_years: number;
}

// engine_boundary.run_efb_underwrite return shape. Non-finite engine values arrive as null.
export interface EFBHeadlineMetrics {
  bond_amount: number | null;
  annual_debt_service: number | null;
  maximum_debt_service: number | null;
  year1_noi: number | null;
  year1_dscr: number | null;
  target_dscr: number | null;
  bond_rate: number | null;
  tax_savings_10yr: number | null;
}

export interface EFBUnderwriteResponse {
  headline_metrics: EFBHeadlineMetrics;
}

export function underwriteEFB(
  req: EFBUnderwriteRequest,
  signal?: AbortSignal,
): Promise<EFBUnderwriteResponse> {
  return request<EFBUnderwriteResponse>('/underwrite/efb', { method: 'POST', body: req, signal });
}

export type ExitCapStrategy = 'core' | 'core_plus' | 'value_add' | 'opportunistic';

export interface ExitCapRequest {
  going_in_cap: number; // decimal, e.g. 0.055
  strategy: ExitCapStrategy;
  forward_treasury?: number | null;
  agency_spread: number;
  neg_leverage_buffer: number;
  comp_implied_cap?: number | null;
}

// engine_boundary.triangulate_exit_cap return shape. method_treasury comes back 0 (not null)
// when no forward treasury was supplied — treat 0 as "method not run" in the UI.
export interface ExitCapResponse {
  method_treasury: number | null;
  method_comp: number | null;
  method_entry_strategy: number | null;
  exit_cap: number | null;
  binding_method: string; // 'entry+strategy' | 'treasury_spread' | 'comp_validation'
}

export function recalcExitCap(req: ExitCapRequest, signal?: AbortSignal): Promise<ExitCapResponse> {
  return request<ExitCapResponse>('/recalc/exit-cap', { method: 'POST', body: req, signal });
}

export interface AgencySizingRequest {
  stabilized_noi: number;
  stabilized_value: number;
  refi_rate: number; // decimal
  amort_years: number;
  target_dscr: number; // ratio
  max_ltv: number; // decimal, e.g. 0.75
  min_debt_yield: number; // decimal, e.g. 0.085
}

// engine_boundary.size_agency_takeout return shape (MIN across the three constraints).
export interface AgencySizingResponse {
  by_dscr: number | null;
  by_ltv: number | null;
  by_debt_yield: number | null;
  max_loan: number | null;
  binding_constraint: string; // 'dscr' | 'ltv' | 'debt_yield'
}

export function recalcAgencySizing(
  req: AgencySizingRequest,
  signal?: AbortSignal,
): Promise<AgencySizingResponse> {
  return request<AgencySizingResponse>('/recalc/agency-sizing', {
    method: 'POST',
    body: req,
    signal,
  });
}

export function sensitivity(
  req: SensitivityRequest,
  signal?: AbortSignal,
): Promise<SensitivityResponse> {
  return request<SensitivityResponse>('/recalc/sensitivity', { method: 'POST', body: req, signal });
}
