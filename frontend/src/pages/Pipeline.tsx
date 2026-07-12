import { useState, useEffect, useMemo, useCallback, useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  FilePlus2,
  RefreshCw,
  AlertTriangle,
  Inbox,
  TrendingUp,
  Building2,
  Landmark,
  Activity,
  Loader2,
  MoreVertical,
  Archive,
  ArchiveRestore,
  Trash2,
} from 'lucide-react';
import {
  listDeals,
  archiveDeal,
  unarchiveDeal,
  deleteDeal,
  ApiError,
  type DealListItem,
} from '../lib/api';
import { Card, Button, Badge, statusTone } from '../components/ui';
import { fmtEM, fmtPct1, fmtUSD, fmtDate, prettyStatus } from '../lib/format';

type Filter = 'all' | 'computed' | 'awaiting_input' | 'gate_failed' | 'draft' | 'archived';
const FILTERS: { key: Filter; label: string }[] = [
  { key: 'all', label: 'All' },
  { key: 'computed', label: 'Computed' },
  { key: 'awaiting_input', label: 'Awaiting Input' },
  { key: 'gate_failed', label: 'Gate Failed' },
  { key: 'draft', label: 'Draft' },
  { key: 'archived', label: 'Archived' },
];

export function Pipeline() {
  const navigate = useNavigate();
  const [deals, setDeals] = useState<DealListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<Filter>('all');

  // Pull EVERYTHING (archived folded in) so the per-status pills + the Archived pill all render
  // from one fetch; the client filters below decide what each view shows.
  const load = useCallback(() => {
    setLoading(true);
    setError(null);
    listDeals({ include_archived: true })
      .then((d) => setDeals(d))
      .catch((e) => {
        if (e instanceof ApiError && e.status === 401) return; // handled globally
        setError(e instanceof Error ? e.message : String(e));
      })
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  // 'all' = every NON-archived deal; 'archived' = only archived; per-status pills match that status.
  const filtered = useMemo(() => {
    if (filter === 'all') return deals.filter((d) => d.status !== 'archived');
    if (filter === 'archived') return deals.filter((d) => d.status === 'archived');
    return deals.filter((d) => d.status === filter);
  }, [deals, filter]);

  // Count of NON-archived deals for the header + the "All" pill (archived never counts there).
  const activeCount = useMemo(() => deals.filter((d) => d.status !== 'archived').length, [deals]);

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-head font-bold text-slate-near">Pipeline</h1>
          <p className="text-sm text-slate/60 mt-1">
            {loading ? 'Loading deals…' : `${activeCount} deal${activeCount === 1 ? '' : 's'}`}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="secondary" icon={RefreshCw} onClick={load} disabled={loading}>
            Refresh
          </Button>
          <Button icon={FilePlus2} onClick={() => navigate('/underwrite')}>
            New Underwrite
          </Button>
        </div>
      </div>

      {/* status filter pills */}
      <div className="flex flex-wrap gap-2">
        {FILTERS.map((f) => {
          // "All" counts only non-archived; every other pill counts its own status.
          const count =
            f.key === 'all' ? activeCount : deals.filter((d) => d.status === f.key).length;
          const active = filter === f.key;
          return (
            <button
              key={f.key}
              onClick={() => setFilter(f.key)}
              className={[
                'px-3 py-1.5 rounded-full text-sm font-label font-semibold transition-colors border',
                active
                  ? 'bg-teal text-offwhite border-teal'
                  : 'bg-white text-slate/70 border-slate/15 hover:border-teal/40 hover:text-teal',
              ].join(' ')}
            >
              {f.label}
              <span className={active ? 'ml-1.5 opacity-80' : 'ml-1.5 text-slate/40'}>{count}</span>
            </button>
          );
        })}
      </div>

      {error && (
        <Card className="p-4 border-danger/30 bg-danger/5">
          <div className="flex items-center gap-2 text-danger text-sm">
            <AlertTriangle className="w-4 h-4" /> {error}
          </div>
        </Card>
      )}

      {loading ? (
        <div className="flex items-center justify-center py-20 text-slate/50">
          <Loader2 className="w-6 h-6 animate-spin mr-2" /> Loading pipeline…
        </div>
      ) : filtered.length === 0 ? (
        <EmptyState filtered={filter !== 'all'} />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map((d) => (
            <DealCard key={d.deal_id} deal={d} onChanged={load} onError={setError} />
          ))}
        </div>
      )}
    </div>
  );
}

function DealCard({
  deal,
  onChanged,
  onError,
}: {
  deal: DealListItem;
  onChanged: () => void;
  onError: (msg: string) => void;
}) {
  const hm = deal.headline_metrics ?? {};
  const isEFB = deal.routing === 'EFB';
  const isArchived = deal.status === 'archived';

  // ACQ headline pair
  const irr = typeof hm.irr === 'number' ? hm.irr : null;
  const em = typeof hm.equity_multiple === 'number' ? hm.equity_multiple : null;
  // EFB headline pair
  const bond = typeof hm.bond_amount === 'number' ? hm.bond_amount : null;
  const dscr = typeof hm.year1_dscr === 'number' ? hm.year1_dscr : null;

  const hasMetrics = isEFB ? bond != null || dscr != null : irr != null || em != null;

  return (
    <Link to={`/deal/${encodeURIComponent(deal.deal_id)}`} className="block group">
      <Card
        className={`relative p-5 h-full transition-shadow group-hover:shadow-cardHover border-t-4 ${
          isEFB ? 'border-t-taupe' : 'border-t-teal'
        }`}
      >
        <CardMenu deal={deal} isArchived={isArchived} onChanged={onChanged} onError={onError} />
        <div className="flex items-start justify-between gap-2 mb-3 pr-8">
          <h3 className="font-head font-bold text-lg text-slate-near leading-tight">
            {deal.deal_name || 'Untitled deal'}
          </h3>
          <Badge tone={isEFB ? 'taupe' : 'teal'}>
            {isEFB && <Landmark className="w-3 h-3" />}
            {deal.routing || '—'}
          </Badge>
        </div>

        <div className="flex items-center gap-2 mb-4">
          <Badge tone={statusTone(deal.status)}>{prettyStatus(deal.status)}</Badge>
          <span className="text-xs text-slate/40">Updated {fmtDate(deal.updated_at)}</span>
        </div>

        {hasMetrics ? (
          <div className="grid grid-cols-2 gap-3 pt-3 border-t border-slate/10">
            {isEFB ? (
              <>
                <Metric
                  label="Bond Proceeds"
                  value={bond != null ? fmtUSD(bond) : '—'}
                  icon={Landmark}
                />
                <Metric label="Year-1 DSCR" value={dscr != null ? fmtEM(dscr) : '—'} icon={Activity} />
              </>
            ) : (
              <>
                <Metric label="IRR" value={irr != null ? fmtPct1(irr) : '—'} icon={TrendingUp} />
                <Metric label="Equity Mult." value={em != null ? fmtEM(em) : '—'} icon={Building2} />
              </>
            )}
          </div>
        ) : (
          <p className="text-xs text-slate/40 pt-3 border-t border-slate/10">
            Not yet computed — open to run / review.
          </p>
        )}
      </Card>
    </Link>
  );
}

// Kebab menu overlaid on a card that is itself a <Link>. Every interactive handler calls
// preventDefault() + stopPropagation() FIRST so a click never triggers the card's navigation.
// Open/close is local useState; an outside pointerdown (or blur) closes it — no new deps.
function CardMenu({
  deal,
  isArchived,
  onChanged,
  onError,
}: {
  deal: DealListItem;
  isArchived: boolean;
  onChanged: () => void;
  onError: (msg: string) => void;
}) {
  const [open, setOpen] = useState(false);
  const [busy, setBusy] = useState(false);
  const menuRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!open) return;
    const onDown = (e: PointerEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener('pointerdown', onDown);
    return () => document.removeEventListener('pointerdown', onDown);
  }, [open]);

  // Run a mutating action, then refresh the list. ApiError messages (e.g. 409 "job running")
  // surface via the page-level error state. `stop` is the event whose default/propagation we kill.
  const act = async (
    e: React.MouseEvent,
    fn: () => Promise<unknown>,
  ) => {
    e.preventDefault();
    e.stopPropagation();
    if (busy) return;
    setBusy(true);
    setOpen(false);
    try {
      await fn();
      onChanged();
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) return; // handled globally
      onError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  };

  const onDelete = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (busy) return;
    if (!window.confirm(`Permanently delete "${deal.deal_name}"? This cannot be undone.`)) {
      setOpen(false);
      return;
    }
    void act(e, () => deleteDeal(deal.deal_id));
  };

  const toggle = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (busy) return;
    setOpen((v) => !v);
  };

  return (
    <div ref={menuRef} className="absolute top-3 right-3 z-10">
      <button
        type="button"
        aria-label="Deal actions"
        aria-haspopup="true"
        aria-expanded={open ? true : undefined}
        onClick={toggle}
        disabled={busy}
        className="p-1 rounded-lg text-slate/40 hover:text-slate hover:bg-slate/5 disabled:opacity-50 transition-colors"
      >
        {busy ? <Loader2 className="w-4 h-4 animate-spin" /> : <MoreVertical className="w-4 h-4" />}
      </button>

      {open && (
        <div
          className="absolute top-full right-0 mt-1 w-40 rounded-xl border border-slate/15 bg-white shadow-cardHover py-1 text-sm"
        >
          {isArchived ? (
            <MenuItem
              icon={ArchiveRestore}
              label="Unarchive"
              onClick={(e) => act(e, () => unarchiveDeal(deal.deal_id))}
            />
          ) : (
            <MenuItem
              icon={Archive}
              label="Archive"
              onClick={(e) => act(e, () => archiveDeal(deal.deal_id))}
            />
          )}
          <MenuItem icon={Trash2} label="Delete" danger onClick={onDelete} />
        </div>
      )}
    </div>
  );
}

function MenuItem({
  icon: Icon,
  label,
  danger,
  onClick,
}: {
  icon: typeof Archive;
  label: string;
  danger?: boolean;
  onClick: (e: React.MouseEvent) => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`w-full flex items-center gap-2 px-3 py-1.5 text-left font-label font-medium transition-colors ${
        danger ? 'text-danger hover:bg-danger/5' : 'text-slate hover:bg-teal-panel/60'
      }`}
    >
      <Icon className="w-3.5 h-3.5 shrink-0" /> {label}
    </button>
  );
}

function Metric({
  label,
  value,
  icon: Icon,
}: {
  label: string;
  value: string;
  icon: typeof TrendingUp;
}) {
  return (
    <div>
      <span className="eyebrow text-slate/50 flex items-center gap-1">
        <Icon className="w-3 h-3" /> {label}
      </span>
      <div className="font-head font-bold text-xl text-teal tnum mt-0.5">{value}</div>
    </div>
  );
}

function EmptyState({ filtered }: { filtered: boolean }) {
  return (
    <Card className="p-12 flex flex-col items-center text-center">
      <div className="w-14 h-14 rounded-full bg-teal-panel flex items-center justify-center mb-4">
        <Inbox className="w-7 h-7 text-teal" />
      </div>
      <h3 className="font-head font-bold text-xl text-slate-near mb-1">
        {filtered ? 'No deals in this view' : 'No deals yet'}
      </h3>
      <p className="text-sm text-slate/60 mb-5 max-w-sm">
        {filtered
          ? 'Try another status filter, or start a fresh underwrite.'
          : 'Start your first underwrite — the analysts will walk you to a CP-1 review.'}
      </p>
      <Link to="/underwrite">
        <Button icon={FilePlus2}>New Underwrite</Button>
      </Link>
    </Card>
  );
}
