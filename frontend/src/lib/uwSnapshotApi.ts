// Typed GET-only client for the read-only UW Snapshot endpoint. Never sends anything but GET.
// The stored shape is a placeholder until the UW Director confirms the real one.
import { API_BASE, ApiError, getAuthToken } from './api';

export interface UnitMixRow {
  unit_type: string;
  units: number | string | null;
  safe_harbor_rent: number | string | null;
  in_place_rent?: number | string | null;
}

export interface T12Line {
  line: string;
  amount: number | string | null;
}

export interface UwSnapshot {
  property_name?: string;
  verdict?: string;
  engine_version?: string;
  unit_mix?: UnitMixRow[];
  seller_t12?: T12Line[];
  seller_t12_noi?: number | string | null;
  stabilized_gpr?: number | string | null;
  stabilized_noi?: number | string | null;
  exempt_dscr?: number | string | null;
}

export interface UwSnapshotView {
  deal_id: string;
  state: 'ready' | 'blank';
  blank_reason: string | null;
  snapshot: UwSnapshot | null;
  read_only: boolean;
}

export async function getUwSnapshot(dealId: string, signal?: AbortSignal): Promise<UwSnapshotView> {
  const headers: Record<string, string> = {};
  const token = getAuthToken();
  if (token) headers['Authorization'] = `Bearer ${token}`;
  const res = await fetch(`${API_BASE}/deals/${encodeURIComponent(dealId)}/uw-snapshot`, {
    method: 'GET',
    headers,
    signal,
  });
  if (!res.ok) throw new ApiError(res.status, `UW Snapshot request failed (${res.status}).`);
  return (await res.json()) as UwSnapshotView;
}
