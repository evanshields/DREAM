import { useEffect, useState } from 'react';
import { Card, Badge } from './ui';
import { getUwSnapshot, type UwSnapshotView } from '../lib/uwSnapshotApi';

// Read-only. Every number is shown exactly as the data gives it (String(value), no rounding, no
// sums, no ratios). Nothing here computes a metric.
const show = (v: unknown): string => (v === null || v === undefined || v === '' ? '—' : String(v));

function Fact({ label, value }: { label: string; value: unknown }) {
  return (
    <div className="min-w-[8rem] flex-1">
      <dt className="text-xs text-slate/60">{label}</dt>
      <dd className="text-base font-semibold break-words">{show(value)}</dd>
    </div>
  );
}

export function UwSnapshotView({ view }: { view: UwSnapshotView }) {
  const snap = view.snapshot;
  if (view.state !== 'ready' || !snap) {
    return (
      <Card className="p-4" >
        <h2 className="font-heading text-base mb-2">UW Snapshot</h2>
        <p data-testid="uw-blank" className="text-sm text-slate/70">
          {view.blank_reason ?? 'No numbers to show.'}
        </p>
        {typeof snap?.verdict === 'string' && snap.verdict && (
          <p className="mt-2 text-sm">
            <span className="text-slate/60">Verdict: </span>
            <Badge tone="neutral">{snap.verdict}</Badge>
          </p>
        )}
        {typeof snap?.engine_version === 'string' && snap.engine_version && (
          <p className="mt-1 text-xs text-slate/60">Engine version: {snap.engine_version}</p>
        )}
      </Card>
    );
  }
  const mix = Array.isArray(snap.unit_mix) ? snap.unit_mix : [];
  const t12 = Array.isArray(snap.seller_t12) ? snap.seller_t12 : [];
  return (
    <Card className="p-4">
      <h2 className="font-heading text-base mb-1">UW Snapshot</h2>
      <p className="text-sm mb-3">
        <Badge tone="neutral">{show(snap.verdict)}</Badge>
        <span className="ml-2 text-xs text-slate/60">Engine version: {show(snap.engine_version)}</span>
      </p>

      <h3 className="text-sm font-semibold mb-1">Unit mix vs safe-harbor rents</h3>
      <div className="overflow-x-auto mb-4">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-xs text-slate/60">
              <th className="py-2 pr-3">Type</th>
              <th className="py-2 pr-3">Units</th>
              <th className="py-2 pr-3">Safe-harbor rent</th>
              <th className="py-2">In-place rent</th>
            </tr>
          </thead>
          <tbody>
            {mix.map((r, i) => (
              <tr key={`${r.unit_type}-${i}`} className="border-t border-slate/10">
                <td className="py-2 pr-3">{show(r.unit_type)}</td>
                <td className="py-2 pr-3">{show(r.units)}</td>
                <td className="py-2 pr-3">{show(r.safe_harbor_rent)}</td>
                <td className="py-2">{show(r.in_place_rent)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <h3 className="text-sm font-semibold mb-1">Seller T-12</h3>
      <dl className="mb-4">
        {t12.map((l, i) => (
          <div key={`${l.line}-${i}`} className="flex justify-between gap-3 border-t border-slate/10 py-2 text-sm">
            <dt>{show(l.line)}</dt>
            <dd className="text-right">{show(l.amount)}</dd>
          </div>
        ))}
        <div className="flex justify-between gap-3 border-t border-slate/20 py-2 text-sm font-semibold">
          <dt>Seller T-12 NOI</dt>
          <dd className="text-right">{show(snap.seller_t12_noi)}</dd>
        </div>
      </dl>

      <h3 className="text-sm font-semibold mb-1">Our stabilized view</h3>
      <dl className="flex flex-wrap gap-4">
        <Fact label="Stabilized GPR" value={snap.stabilized_gpr} />
        <Fact label="Stabilized NOI" value={snap.stabilized_noi} />
        <Fact label="Exempt DSCR" value={snap.exempt_dscr} />
      </dl>
    </Card>
  );
}

export function UwSnapshotPanel({ dealId }: { dealId: string }) {
  const [view, setView] = useState<UwSnapshotView | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const ctl = new AbortController();
    setView(null);
    setError(null);
    getUwSnapshot(dealId, ctl.signal)
      .then(setView)
      .catch((e) => {
        if (ctl.signal.aborted) return;
        setError(e instanceof Error ? e.message : String(e));
      });
    return () => ctl.abort();
  }, [dealId]);

  if (error) {
    return (
      <Card className="p-4">
        <h2 className="font-heading text-base mb-2">UW Snapshot</h2>
        <p className="text-sm text-slate/70">Could not load the snapshot. {error}</p>
      </Card>
    );
  }
  if (!view) return null;
  return <UwSnapshotView view={view} />;
}
