// Typed GET-only client for the read-only UW Snapshot endpoint. Never sends anything but GET.
// The stored shape is a placeholder until the UW Director confirms the real one.
import { ApiError, request } from './api';

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

const isRecord = (v: unknown): v is Record<string, unknown> =>
  typeof v === 'object' && v !== null && !Array.isArray(v);
const isScalar = (v: unknown): boolean =>
  v === null || v === undefined || typeof v === 'string' || (typeof v === 'number' && Number.isFinite(v));

const BAD_SHAPE = 'The snapshot is not in the expected shape, so it is not shown.';
const COLLECTIONS = ['unit_mix', 'seller_t12'] as const;
const STRING_FIELDS = ['property_name', 'verdict', 'engine_version'] as const;
const SCALAR_FIELDS = ['seller_t12_noi', 'stabilized_gpr', 'stabilized_noi', 'exempt_dscr'] as const;

export type ParsedView = { ok: true; view: UwSnapshotView } | { ok: false; message: string };

// Runtime check before anything reaches React. Rejects the whole view when any retained string is
// not a string, a collection is not an array, a row is not an object or a cell is not a scalar.
export function parseUwSnapshotView(raw: unknown): ParsedView {
  const bad: ParsedView = { ok: false, message: BAD_SHAPE };
  if (!isRecord(raw)) return bad;
  if (raw.state !== 'ready' && raw.state !== 'blank') return bad;
  if (typeof raw.deal_id !== 'string') return bad;
  if (raw.blank_reason !== null && raw.blank_reason !== undefined && typeof raw.blank_reason !== 'string') return bad;
  const snap = raw.snapshot;
  if (snap !== null && snap !== undefined) {
    if (!isRecord(snap)) return bad;
    for (const k of STRING_FIELDS) {
      if (snap[k] !== undefined && snap[k] !== null && typeof snap[k] !== 'string') return bad;
    }
    for (const k of SCALAR_FIELDS) if (!isScalar(snap[k])) return bad;
    for (const k of COLLECTIONS) {
      const rows = snap[k];
      if (rows === undefined || rows === null) continue;
      if (!Array.isArray(rows)) return bad;
      for (const row of rows) {
        if (!isRecord(row) || !Object.values(row).every(isScalar)) return bad;
      }
    }
  }
  return { ok: true, view: raw as unknown as UwSnapshotView };
}

export async function getUwSnapshot(dealId: string, signal?: AbortSignal): Promise<UwSnapshotView> {
  // Shared request contract: auth header, 401 handler, error mapping.
  const raw = await request<unknown>(`/deals/${encodeURIComponent(dealId)}/uw-snapshot`, { signal });
  const parsed = parseUwSnapshotView(raw);
  if (!parsed.ok) throw new ApiError(502, parsed.message);
  return parsed.view;
}
