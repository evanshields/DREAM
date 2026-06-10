import { useState, useEffect, useMemo, useCallback } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  FilePlus2,
  RefreshCw,
  AlertTriangle,
  Inbox,
  TrendingUp,
  Building2,
  Loader2,
} from 'lucide-react';
import { listDeals, ApiError, type DealListItem } from '../lib/api';
import { Card, Button, Badge, statusTone } from '../components/ui';
import { fmtEM, fmtPct1, fmtDate, prettyStatus } from '../lib/format';

type Filter = 'all' | 'computed' | 'awaiting_input' | 'gate_failed' | 'draft';
const FILTERS: { key: Filter; label: string }[] = [
  { key: 'all', label: 'All' },
  { key: 'computed', label: 'Computed' },
  { key: 'awaiting_input', label: 'Awaiting Input' },
  { key: 'gate_failed', label: 'Gate Failed' },
  { key: 'draft', label: 'Draft' },
];

export function Pipeline() {
  const navigate = useNavigate();
  const [deals, setDeals] = useState<DealListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<Filter>('all');

  const load = useCallback(() => {
    setLoading(true);
    setError(null);
    listDeals()
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

  const filtered = useMemo(
    () => (filter === 'all' ? deals : deals.filter((d) => d.status === filter)),
    [deals, filter],
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-head font-bold text-slate-near">Pipeline</h1>
          <p className="text-sm text-slate/60 mt-1">
            {loading ? 'Loading deals…' : `${deals.length} deal${deals.length === 1 ? '' : 's'}`}
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
          const count =
            f.key === 'all' ? deals.length : deals.filter((d) => d.status === f.key).length;
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
            <DealCard key={d.deal_id} deal={d} />
          ))}
        </div>
      )}
    </div>
  );
}

function DealCard({ deal }: { deal: DealListItem }) {
  const hm = deal.headline_metrics ?? {};
  const irr = typeof hm.irr === 'number' ? hm.irr : null;
  const em = typeof hm.equity_multiple === 'number' ? hm.equity_multiple : null;

  return (
    <Link to={`/deal/${encodeURIComponent(deal.deal_id)}`} className="block group">
      <Card className="p-5 h-full transition-shadow group-hover:shadow-cardHover border-t-4 border-t-teal">
        <div className="flex items-start justify-between gap-2 mb-3">
          <h3 className="font-head font-bold text-lg text-slate-near leading-tight">
            {deal.deal_name || 'Untitled deal'}
          </h3>
          <Badge tone={deal.routing === 'EFB' ? 'taupe' : 'teal'}>{deal.routing || '—'}</Badge>
        </div>

        <div className="flex items-center gap-2 mb-4">
          <Badge tone={statusTone(deal.status)}>{prettyStatus(deal.status)}</Badge>
          <span className="text-xs text-slate/40">Updated {fmtDate(deal.updated_at)}</span>
        </div>

        {irr != null || em != null ? (
          <div className="grid grid-cols-2 gap-3 pt-3 border-t border-slate/10">
            <Metric label="IRR" value={irr != null ? fmtPct1(irr) : '—'} icon={TrendingUp} />
            <Metric label="Equity Mult." value={em != null ? fmtEM(em) : '—'} icon={Building2} />
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
