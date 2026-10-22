import { useState, type ReactNode } from 'react';
import type { MonoRecord } from '../../lib/monoApi';

export function monoText(value: unknown): string {
  if (value === undefined) return 'Unknown';
  if (value === null) return 'Null';
  if (value === '') return 'Empty text';
  if (typeof value === 'object') return JSON.stringify(value, null, 2);
  return String(value);
}

export function monoValue(value: unknown, unit: unknown): string {
  if (typeof value !== 'number' || !Number.isFinite(value)) return monoText(value);
  if (unit === '%' || unit === 'rate') return new Intl.NumberFormat('en-US', { style: 'percent', maximumFractionDigits: 2 }).format(value);
  if (unit === '$' || unit === 'usd' || unit === 'USD') return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 2 }).format(value);
  return new Intl.NumberFormat('en-US', { maximumFractionDigits: 6 }).format(value);
}

export function asRecord(value: unknown): MonoRecord {
  return value !== null && typeof value === 'object' && !Array.isArray(value) ? value as MonoRecord : {};
}

export function Evidence({ value, label = 'Evidence' }: { value: unknown; label?: string }) {
  return <pre aria-label={label} className="whitespace-pre-wrap break-words rounded-lg bg-offwhite p-3 text-xs text-slate/80 max-h-80 overflow-auto">{monoText(value)}</pre>;
}

export function Details({ title, children, open = false }: { title: string; children: ReactNode; open?: boolean }) {
  const [loaded, setLoaded] = useState(open);
  return <details open={open || undefined} onToggle={(event) => { if (event.currentTarget.open) setLoaded(true); }} className="rounded-lg border border-slate/10 bg-white">
    <summary className="cursor-pointer px-4 py-3 text-sm font-semibold text-teal focus-visible:outline-teal">{title}</summary>
    {(loaded || open) && <div className="px-4 pb-4 space-y-3">{children}</div>}
  </details>;
}

export function ProblemList({ values, empty }: { values: unknown[]; empty?: string }) {
  if (!values.length) return empty ? <p className="text-sm text-slate/60">{empty}</p> : null;
  return <ul className="space-y-2 text-sm">{values.map((value, index) => <li key={index} className="rounded-lg border border-warn/25 bg-warn/5 p-3 whitespace-pre-wrap break-words">{monoText(value)}</li>)}</ul>;
}
