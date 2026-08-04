import { useEffect, useRef, useState } from 'react';
import { RefreshCw, CheckCircle2, AlertTriangle } from 'lucide-react';
import { ApiError } from '../lib/api';
import { Badge } from './ui';
import { fmtUSD, fmtPct, fmtEM } from '../lib/format';

// ---------------------------------------------------------------------------
// Shared live-recalc primitives (extracted from BondScreen so the EFB sizing
// panel can render on both /bond-screen and the EFB deal detail):
//   - Kind + edit-string helpers (percent entered as 5 => 0.05, ratio as-is)
//   - useLiveCalc: run once immediately, then debounce 450ms per edit
//   - StatusLine: recalculating / error / up-to-date indicator
//   - NumField: draft-buffered numeric input (commits on blur/Enter)
// ---------------------------------------------------------------------------

export type Kind = 'usd' | 'pct' | 'int' | 'ratio';

export function displayValue(kind: Kind, v: number | null | undefined): string {
  if (v == null) return '—';
  if (kind === 'usd') return fmtUSD(v);
  if (kind === 'pct') return fmtPct(v);
  if (kind === 'ratio') return fmtEM(v);
  return `${v}`;
}

export function toEditString(kind: Kind, v: number | null | undefined): string {
  if (v == null) return '';
  if (kind === 'pct') return (v * 100).toString();
  return v.toString();
}

// '' -> null (field cleared); invalid -> undefined (ignore the commit)
export function fromEditString(kind: Kind, s: string): number | null | undefined {
  if (s.trim() === '') return null;
  const n = Number(s);
  if (!Number.isFinite(n)) return undefined;
  if (kind === 'pct') return n / 100;
  if (kind === 'int') return Math.round(n);
  return n;
}

// --- shared live-calc hook: run once immediately, then debounce 450ms ------

export interface LiveCalcState<Res> {
  result: Res | null;
  loading: boolean;
  error: string | null;
}

export function useLiveCalc<Req, Res>(
  fn: (req: Req, signal?: AbortSignal) => Promise<Res>,
  req: Req,
): LiveCalcState<Res> {
  const [result, setResult] = useState<Res | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);
  const debounceRef = useRef<number | null>(null);
  const firstRef = useRef(true);

  useEffect(() => {
    const run = () => {
      abortRef.current?.abort();
      const ctrl = new AbortController();
      abortRef.current = ctrl;
      setLoading(true);
      setError(null);
      fn(req, ctrl.signal)
        .then((res) => {
          if (ctrl.signal.aborted) return;
          setResult(res);
          setLoading(false);
        })
        .catch((e: unknown) => {
          if (ctrl.signal.aborted) return;
          if (e instanceof ApiError && e.status === 401) return;
          setError(e instanceof Error ? e.message : String(e));
          setLoading(false);
        });
    };
    if (firstRef.current) {
      firstRef.current = false;
      run();
    } else {
      if (debounceRef.current) window.clearTimeout(debounceRef.current);
      debounceRef.current = window.setTimeout(run, 450);
    }
  }, [fn, req]);

  // abort in-flight + cancel pending debounce on unmount only
  useEffect(
    () => () => {
      abortRef.current?.abort();
      if (debounceRef.current) window.clearTimeout(debounceRef.current);
    },
    [],
  );

  return { result, loading, error };
}

// --- status line (recalculating / error / up to date) ----------------------

export function StatusLine({ loading, error }: { loading: boolean; error: string | null }) {
  return (
    <div className="h-5 flex items-center">
      {loading ? (
        <span className="inline-flex items-center text-xs font-medium text-teal">
          <RefreshCw className="w-3.5 h-3.5 mr-1.5 animate-spin" /> recalculating…
        </span>
      ) : error ? (
        <span className="inline-flex items-center text-xs font-medium text-danger">
          <AlertTriangle className="w-3.5 h-3.5 mr-1.5" /> {error}
        </span>
      ) : (
        <span className="inline-flex items-center text-xs font-medium text-ok">
          <CheckCircle2 className="w-3.5 h-3.5 mr-1.5" /> up to date
        </span>
      )}
    </div>
  );
}

// --- generic numeric field (draft-buffered; commits on blur/Enter) ---------

export interface NumFieldProps {
  label: string;
  kind: Kind;
  value: number | null;
  hint?: string;
  optional?: boolean;
  onCommit: (v: number | null) => void;
}

export function NumField({ label, kind, value, hint, optional, onCommit }: NumFieldProps) {
  const [draft, setDraft] = useState<string | null>(null);

  const commit = (raw: string) => {
    const parsed = fromEditString(kind, raw);
    setDraft(null);
    if (parsed === undefined) return; // unparseable, keep prior value
    if (parsed === null && !optional) return; // required field cleared, keep prior value
    onCommit(parsed);
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-1.5">
        <label className="text-sm font-semibold text-slate">{label}</label>
        <Badge tone="neutral">{kind === 'pct' ? '%' : kind === 'usd' ? 'USD' : kind === 'ratio' ? 'x' : '#'}</Badge>
      </div>
      <div className="flex items-center gap-2">
        <input
          className="input"
          type="number"
          step={kind === 'pct' ? '0.01' : kind === 'ratio' ? '0.01' : kind === 'int' ? '1' : '1000'}
          placeholder={optional ? 'optional' : undefined}
          value={draft ?? toEditString(kind, value)}
          onChange={(e) => setDraft(e.target.value)}
          onBlur={(e) => commit(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') (e.target as HTMLInputElement).blur();
          }}
          aria-label={label}
        />
        <span className="text-xs text-slate/50 whitespace-nowrap min-w-[56px] text-right tnum">
          {displayValue(kind, value)}
        </span>
      </div>
      {hint && <p className="text-[11px] text-slate/50 mt-1 leading-tight">{hint}</p>}
    </div>
  );
}
