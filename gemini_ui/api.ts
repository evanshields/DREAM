// Lightweight, LLM-free API client for the deterministic recalc endpoints.
// All calls hit the FastAPI backend under a configurable base (default '/api',
// same-origin in prod behind Caddy). NEVER calls an LLM — these endpoints
// (/api/recalc, /api/recalc/sensitivity) are guaranteed LLM-free server-side.

// Configurable base URL. In prod the UI is served same-origin with the API, so
// the relative '/api' resolves correctly behind Caddy. Override via Vite env
// (VITE_API_BASE) for split-origin dev if ever needed.
export const API_BASE: string =
  ((import.meta as any)?.env?.VITE_API_BASE as string | undefined)?.replace(/\/$/, '') || '/api';

// --- ACQ recalc request shape — mirrors backend ACQRecalcRequest exactly ---
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

  // optional / unused by the dashboard but part of the contract
  gpr_series?: number[] | null;
  egi_series?: number[] | null;
  opex_series?: number[] | null;
  vacancy_series?: number[] | null;
  debt_service?: number[] | null;
  years?: number;
}

// Headline metrics returned by run_acq_underwrite (floats).
export interface HeadlineMetrics {
  irr: number;
  equity_multiple: number;
  coc_stabilized: number;
  exit_value: number;
  dscr_series?: number[];
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

// --- auth token (the recalc/jobs routers are auth-gated in production) -----
// The login flow (Google sign-in or POST /api/auth/login) stores the bearer token here;
// every API call attaches it. Kept in localStorage so a page reload stays signed in.
const TOKEN_KEY = 'dream_token';

export function setAuthToken(token: string | null): void {
  try {
    if (token) localStorage.setItem(TOKEN_KEY, token);
    else localStorage.removeItem(TOKEN_KEY);
  } catch {
    /* storage unavailable (SSR/incognito) — calls just go unauthenticated */
  }
}

export function getAuthToken(): string | null {
  try {
    return localStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
}

async function postJson<T>(path: string, body: unknown, signal?: AbortSignal): Promise<T> {
  const token = getAuthToken();
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify(body),
    signal,
  });
  if (!res.ok) {
    let detail = `${res.status} ${res.statusText}`;
    try {
      const j = await res.json();
      if (j?.detail) detail = typeof j.detail === 'string' ? j.detail : JSON.stringify(j.detail);
    } catch {
      /* non-JSON error body — keep status text */
    }
    throw new Error(detail);
  }
  return res.json() as Promise<T>;
}

export function recalc(req: ACQRecalcRequest, signal?: AbortSignal): Promise<RecalcResponse> {
  return postJson<RecalcResponse>('/recalc', req, signal);
}

export function sensitivity(req: SensitivityRequest, signal?: AbortSignal): Promise<SensitivityResponse> {
  return postJson<SensitivityResponse>('/recalc/sensitivity', req, signal);
}
