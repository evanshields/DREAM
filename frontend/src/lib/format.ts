// Shared display formatters (data cells, headline numbers). Used across screens.

export const fmtUSD = (v: number): string =>
  v >= 1_000_000
    ? `$${(v / 1_000_000).toFixed(2)}M`
    : `$${v.toLocaleString('en-US', { maximumFractionDigits: 0 })}`;

export const fmtUSDFull = (v: number): string =>
  `$${v.toLocaleString('en-US', { maximumFractionDigits: 0 })}`;

export const fmtPct = (v: number): string => `${(v * 100).toFixed(2)}%`;
export const fmtPct1 = (v: number): string => `${(v * 100).toFixed(1)}%`;
export const fmtEM = (v: number): string => `${v.toFixed(2)}x`;

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
