// Shared display formatters (data cells, headline numbers). Used across screens.

// A missing or non-finite number must show a dash, never "NaN%" or "$NaN".
const DASH = '—';
const finite = (v: unknown): v is number => typeof v === 'number' && Number.isFinite(v);

export const fmtUSD = (v: number | null | undefined): string =>
  !finite(v)
    ? DASH
    : v >= 1_000_000
      ? `$${(v / 1_000_000).toFixed(2)}M`
      : `$${v.toLocaleString('en-US', { maximumFractionDigits: 0 })}`;

export const fmtUSDFull = (v: number | null | undefined): string =>
  finite(v) ? `$${v.toLocaleString('en-US', { maximumFractionDigits: 0 })}` : DASH;

export const fmtPct = (v: number | null | undefined): string => (finite(v) ? `${(v * 100).toFixed(2)}%` : DASH);
export const fmtPct1 = (v: number | null | undefined): string => (finite(v) ? `${(v * 100).toFixed(1)}%` : DASH);
export const fmtEM = (v: number | null | undefined): string => (finite(v) ? `${v.toFixed(2)}x` : DASH);

export function fmtDate(iso: string): string {
  if (!iso) return '—';
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

export function fmtDateTime(iso: string): string {
  if (!iso) return '—';
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return d.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  });
}

// human-friendly status label
export function prettyStatus(s: string): string {
  return s
    .split('_')
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ');
}
