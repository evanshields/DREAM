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
  LayoutGrid,
  Table as TableIcon,
  Trello,
  ArrowUp,
  ArrowDown,
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
import { useAuth } from '../auth/AuthContext';
import { useToast } from '../contexts/ToastContext';
import { fmtEM, fmtPct1, fmtUSD, fmtDate, prettyStatus } from '../lib/format';

// ---------------------------------------------------------------------------
// View state (Phase 5, Session 3): layout + preset filter + sort, persisted in
// localStorage (2 users, no backend view store — the borrow list's guidance).
// ---------------------------------------------------------------------------

type ViewMode = 'cards' | 'table' | 'kanban';
type PresetKey = 'all' | 'my_open' | 'efb' | 'needs_attention' | 'archived';
type SortField = 'updated_at' | 'deal_name' | 'status' | 'routing';
type SortDir = 'asc' | 'desc';

interface ViewState {
  view: ViewMode;
  preset: PresetKey;
  sortField: SortField;
  sortDir: SortDir;
}

const VIEW_KEY = 'dream_pipeline_view';
const DEFAULT_VIEW: ViewState = {
  view: 'cards',
  preset: 'all',
  sortField: 'updated_at',
  sortDir: 'desc',
};

function loadViewState(): ViewState {
  try {
    const raw = localStorage.getItem(VIEW_KEY);
    if (!raw) return DEFAULT_VIEW;
    const p = JSON.parse(raw) as Partial<ViewState>;
    return {
      view: (['cards', 'table', 'kanban'] as ViewMode[]).includes(p.view as ViewMode)
        ? (p.view as ViewMode)
        : DEFAULT_VIEW.view,
      preset: (['all', 'my_open', 'efb', 'needs_attention', 'archived'] as PresetKey[]).includes(
        p.preset as PresetKey,
      )
        ? (p.preset as PresetKey)
        : DEFAULT_VIEW.preset,
      sortField: (['updated_at', 'deal_name', 'status', 'routing'] as SortField[]).includes(
        p.sortField as SortField,
      )
        ? (p.sortField as SortField)
        : DEFAULT_VIEW.sortField,
      sortDir: p.sortDir === 'asc' ? 'asc' : 'desc',
    };
  } catch {
    return DEFAULT_VIEW;
  }
}

// The 3 hardcoded presets (+ All + Archived), each a predicate over a deal (owner passed for "mine").
const PRESETS: { key: PresetKey; label: string; pred: (d: DealListItem, me: string) => boolean }[] = [
  { key: 'all', label: 'All', pred: (d) => d.status !== 'archived' },
  {
    key: 'my_open',
    label: 'My Open',
    pred: (d, me) => d.owner.toLowerCase() === me && d.status !== 'archived',
  },
  { key: 'efb', label: 'EFB Pipeline', pred: (d) => d.routing === 'EFB' && d.status !== 'archived' },
  {
    key: 'needs_attention',
    label: 'Needs Attention',
    pred: (d) => d.status === 'gate_failed' || d.status === 'awaiting_input',
  },
  { key: 'archived', label: 'Archived', pred: (d) => d.status === 'archived' },
];

const SORT_LABELS: Record<SortField, string> = {
  updated_at: 'Updated',
  deal_name: 'Name',
  status: 'Status',
  routing: 'Routing',
};

function compareDeals(a: DealListItem, b: DealListItem, field: SortField, dir: SortDir): number {
  const s = dir === 'asc' ? 1 : -1;
  switch (field) {
    case 'deal_name':
      return s * (a.deal_name || '').localeCompare(b.deal_name || '');
    case 'status':
      return s * a.status.localeCompare(b.status);
    case 'routing':
      return s * a.routing.localeCompare(b.routing);
    default:
      // ISO-8601 strings sort lexically == chronologically
      return s * (a.updated_at || '').localeCompare(b.updated_at || '');
  }
}

export function Pipeline() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const me = (user?.email ?? '').toLowerCase();
  const { showToast } = useToast();
  const [deals, setDeals] = useState<DealListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [vs, setVs] = useState<ViewState>(loadViewState);
  // persist any view change
  useEffect(() => {
    try {
      localStorage.setItem(VIEW_KEY, JSON.stringify(vs));
    } catch {
      /* storage unavailable — view just won't persist */
    }
  }, [vs]);
  const patchVs = useCallback((p: Partial<ViewState>) => setVs((v) => ({ ...v, ...p })), []);

  // Pull EVERYTHING (archived folded in) from one fetch; the client decides what each view shows.
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

  // Undo-delete (Phase 5): remove optimistically, show a 6s "Deleted. Undo" toast, and fire the
  // REAL delete only when the countdown completes (onExpire) — so Undo needs zero backend. A 409
  // (job running) restores the list + surfaces the error.
  const handleDelete = useCallback(
    (deal: DealListItem) => {
      setDeals((prev) => prev.filter((d) => d.deal_id !== deal.deal_id));
      showToast({
        message: `Deleted “${deal.deal_name || 'Untitled deal'}”`,
        tone: 'danger',
        action: { label: 'Undo', onClick: () => load() },
        dedupeKey: `del-deal-${deal.deal_id}`,
        onExpire: () => {
          deleteDeal(deal.deal_id).catch((e) => {
            load();
            if (e instanceof ApiError && e.status === 401) return;
            setError(e instanceof Error ? e.message : String(e));
          });
        },
      });
    },
    [showToast, load],
  );

  // Archive / unarchive helper (kanban drag + table actions share it).
  const runAction = useCallback(
    async (fn: () => Promise<unknown>) => {
      try {
        await fn();
        load();
      } catch (e) {
        if (e instanceof ApiError && e.status === 401) return;
        setError(e instanceof Error ? e.message : String(e));
      }
    },
    [load],
  );

  const activePreset = PRESETS.find((p) => p.key === vs.preset) ?? PRESETS[0];

  // Cards + table: preset-filtered then sorted. Kanban ignores preset/sort (it's a status board
  // over every deal, with its own Archived column).
  const filtered = useMemo(
    () => deals.filter((d) => activePreset.pred(d, me)).sort((a, b) =>
      compareDeals(a, b, vs.sortField, vs.sortDir),
    ),
    [deals, activePreset, me, vs.sortField, vs.sortDir],
  );

  const activeCount = useMemo(() => deals.filter((d) => d.status !== 'archived').length, [deals]);
  const isKanban = vs.view === 'kanban';

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-head font-bold text-slate-near">Pipeline</h1>
          <p className="text-sm text-slate/60 mt-1">
            {loading ? 'Loading deals…' : `${activeCount} active deal${activeCount === 1 ? '' : 's'}`}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <ViewToggle view={vs.view} onChange={(view) => patchVs({ view })} />
          <Button variant="secondary" icon={RefreshCw} onClick={load} disabled={loading}>
            <span className="hidden sm:inline">Refresh</span>
          </Button>
          <Button icon={FilePlus2} onClick={() => navigate('/underwrite')}>
            <span className="hidden sm:inline">New Underwrite</span>
          </Button>
        </div>
      </div>

      {/* preset chips + sort (cards/table only — kanban is its own status board) */}
      {!isKanban && (
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex flex-wrap gap-2">
            {PRESETS.map((p) => {
              const count = deals.filter((d) => p.pred(d, me)).length;
              const active = vs.preset === p.key;
              return (
                <button
                  key={p.key}
                  onClick={() => patchVs({ preset: p.key })}
                  className={[
                    'px-3 py-1.5 rounded-full text-sm font-label font-semibold transition-colors border',
                    active
                      ? 'bg-teal text-offwhite border-teal'
                      : 'bg-white text-slate/70 border-slate/15 hover:border-teal/40 hover:text-teal',
                  ].join(' ')}
                >
                  {p.label}
                  <span className={active ? 'ml-1.5 opacity-80' : 'ml-1.5 text-slate/40'}>
                    {count}
                  </span>
                </button>
              );
            })}
          </div>
          <SortControl
            field={vs.sortField}
            dir={vs.sortDir}
            onField={(sortField) => patchVs({ sortField })}
            onToggleDir={() => patchVs({ sortDir: vs.sortDir === 'asc' ? 'desc' : 'asc' })}
          />
        </div>
      )}

      {error && (
        <Card className="p-4 border-danger/30 bg-danger/5">
          <div className="flex items-center gap-2 text-danger text-sm">
            <AlertTriangle className="w-4 h-4" /> {error}
          </div>
        </Card>
      )}

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <SkeletonCard key={i} />
          ))}
        </div>
      ) : isKanban ? (
        <KanbanBoard
          deals={deals}
          onChanged={load}
          onError={setError}
          onDelete={handleDelete}
          onAction={runAction}
        />
      ) : filtered.length === 0 ? (
        <EmptyState filtered={vs.preset !== 'all'} />
      ) : vs.view === 'table' ? (
        <DealTable
          deals={filtered}
          sortField={vs.sortField}
          sortDir={vs.sortDir}
          onSort={(sortField) =>
            patchVs(
              vs.sortField === sortField
                ? { sortDir: vs.sortDir === 'asc' ? 'desc' : 'asc' }
                : { sortField, sortDir: 'asc' },
            )
          }
          onDelete={handleDelete}
          onAction={runAction}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map((d) => (
            <DealCard
              key={d.deal_id}
              deal={d}
              onChanged={load}
              onError={setError}
              onDelete={handleDelete}
            />
          ))}
        </div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// View toggle + sort control
// ---------------------------------------------------------------------------

function ViewToggle({ view, onChange }: { view: ViewMode; onChange: (v: ViewMode) => void }) {
  const opts: { key: ViewMode; icon: typeof LayoutGrid; label: string }[] = [
    { key: 'cards', icon: LayoutGrid, label: 'Cards' },
    { key: 'table', icon: TableIcon, label: 'Table' },
    { key: 'kanban', icon: Trello, label: 'Board' },
  ];
  return (
    <div className="inline-flex rounded-lg border border-slate/15 bg-white p-0.5" role="tablist">
      {opts.map((o) => {
        const Icon = o.icon;
        const active = view === o.key;
        return (
          <button
            key={o.key}
            role="tab"
            aria-selected={active}
            title={o.label}
            onClick={() => onChange(o.key)}
            className={`inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-md text-xs font-label font-semibold transition-colors ${
              active ? 'bg-teal text-offwhite' : 'text-slate/60 hover:text-teal'
            }`}
          >
            <Icon className="w-3.5 h-3.5" />
            <span className="hidden lg:inline">{o.label}</span>
          </button>
        );
      })}
    </div>
  );
}

function SortControl({
  field,
  dir,
  onField,
  onToggleDir,
}: {
  field: SortField;
  dir: SortDir;
  onField: (f: SortField) => void;
  onToggleDir: () => void;
}) {
  return (
    <div className="flex items-center gap-1.5">
      <span className="text-xs text-slate/45 font-label uppercase tracking-wide">Sort</span>
      <select
        value={field}
        onChange={(e) => onField(e.target.value as SortField)}
        className="rounded-lg border border-slate/15 bg-white px-2 py-1.5 text-xs text-slate focus:outline-none focus:ring-2 focus:ring-teal"
      >
        {(Object.keys(SORT_LABELS) as SortField[]).map((f) => (
          <option key={f} value={f}>
            {SORT_LABELS[f]}
          </option>
        ))}
      </select>
      <button
        type="button"
        onClick={onToggleDir}
        aria-label={dir === 'asc' ? 'Ascending' : 'Descending'}
        title={dir === 'asc' ? 'Ascending' : 'Descending'}
        className="rounded-lg border border-slate/15 bg-white p-1.5 text-slate/60 hover:text-teal transition-colors"
      >
        {dir === 'asc' ? <ArrowUp className="w-3.5 h-3.5" /> : <ArrowDown className="w-3.5 h-3.5" />}
      </button>
    </div>
  );
}

function DealCard({
  deal,
  onChanged,
  onError,
  onDelete,
}: {
  deal: DealListItem;
  onChanged: () => void;
  onError: (msg: string) => void;
  onDelete: (deal: DealListItem) => void;
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
        <CardMenu
          deal={deal}
          isArchived={isArchived}
          onChanged={onChanged}
          onError={onError}
          onDelete={onDelete}
        />
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
  onDelete,
}: {
  deal: DealListItem;
  isArchived: boolean;
  onChanged: () => void;
  onError: (msg: string) => void;
  onDelete: (deal: DealListItem) => void;
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

  // Delete = optimistic remove + 6s "Undo" toast (the real DELETE is deferred to the toast's
  // onExpire, owned by the Pipeline). No confirm popup — Undo is the safety net.
  const onDeleteClick = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (busy) return;
    setOpen(false);
    onDelete(deal);
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
          <MenuItem icon={Trash2} label="Delete" danger onClick={onDeleteClick} />
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

// Loading placeholder shaped like a DealCard (replaces the spinner — the layout doesn't jump when
// real cards arrive). Pure CSS pulse; no data.
function SkeletonCard() {
  return (
    <Card className="p-5 h-full border-t-4 border-t-slate/10">
      <div className="animate-pulse">
        <div className="flex items-start justify-between gap-2 mb-3">
          <div className="h-5 bg-slate/10 rounded w-1/2" />
          <div className="h-5 bg-slate/10 rounded-full w-12" />
        </div>
        <div className="flex items-center gap-2 mb-4">
          <div className="h-5 bg-slate/10 rounded-full w-20" />
          <div className="h-3 bg-slate/8 rounded w-16" />
        </div>
        <div className="grid grid-cols-2 gap-3 pt-3 border-t border-slate/10">
          <div>
            <div className="h-2.5 bg-slate/8 rounded w-12 mb-2" />
            <div className="h-6 bg-slate/10 rounded w-16" />
          </div>
          <div>
            <div className="h-2.5 bg-slate/8 rounded w-12 mb-2" />
            <div className="h-6 bg-slate/10 rounded w-16" />
          </div>
        </div>
      </div>
    </Card>
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
          ? 'Nothing matches this filter — try another preset, or start a fresh underwrite.'
          : 'Start your first underwrite — the analysts will walk you to a CP-1 review.'}
      </p>
      <Link to="/underwrite">
        <Button icon={FilePlus2}>New Underwrite</Button>
      </Link>
    </Card>
  );
}

// The one key metric pair a table row / compact view surfaces, routing-aware.
function dealKeyMetric(d: DealListItem): string {
  const hm = d.headline_metrics ?? {};
  if (d.routing === 'EFB') {
    const bond = typeof hm.bond_amount === 'number' ? fmtUSD(hm.bond_amount) : null;
    const dscr = typeof hm.year1_dscr === 'number' ? `${fmtEM(hm.year1_dscr)} DSCR` : null;
    const parts = [bond, dscr].filter(Boolean);
    return parts.length ? parts.join(' · ') : '—';
  }
  const irr = typeof hm.irr === 'number' ? `${fmtPct1(hm.irr)} IRR` : null;
  const em = typeof hm.equity_multiple === 'number' ? fmtEM(hm.equity_multiple) : null;
  const parts = [irr, em].filter(Boolean);
  return parts.length ? parts.join(' · ') : '—';
}

// ---------------------------------------------------------------------------
// Table view — hand-rolled <table> (no library), clickable sort headers, hover-
// revealed row actions. Rows navigate to the deal.
// ---------------------------------------------------------------------------

function DealTable({
  deals,
  sortField,
  sortDir,
  onSort,
  onDelete,
  onAction,
}: {
  deals: DealListItem[];
  sortField: SortField;
  sortDir: SortDir;
  onSort: (f: SortField) => void;
  onDelete: (d: DealListItem) => void;
  onAction: (fn: () => Promise<unknown>) => void;
}) {
  const navigate = useNavigate();

  const SortHead = ({ field, label, className }: { field: SortField; label: string; className?: string }) => (
    <th className={`text-left font-label text-xs font-semibold uppercase tracking-wide text-slate/50 px-4 py-3 ${className ?? ''}`}>
      <button
        type="button"
        onClick={() => onSort(field)}
        className="inline-flex items-center gap-1 hover:text-teal transition-colors"
      >
        {label}
        {sortField === field &&
          (sortDir === 'asc' ? <ArrowUp className="w-3 h-3" /> : <ArrowDown className="w-3 h-3" />)}
      </button>
    </th>
  );

  return (
    <Card className="overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full text-sm min-w-[640px]">
          <thead className="border-b border-slate/10 bg-slate/[0.015]">
            <tr>
              <SortHead field="deal_name" label="Deal" />
              <SortHead field="routing" label="Routing" />
              <SortHead field="status" label="Status" />
              <th className="text-left font-label text-xs font-semibold uppercase tracking-wide text-slate/50 px-4 py-3">
                Key Metric
              </th>
              <SortHead field="updated_at" label="Updated" />
              <th className="w-16 px-4 py-3" aria-label="Actions" />
            </tr>
          </thead>
          <tbody className="divide-y divide-slate/8">
            {deals.map((d) => {
              const isEFB = d.routing === 'EFB';
              const isArchived = d.status === 'archived';
              return (
                <tr
                  key={d.deal_id}
                  onClick={() => navigate(`/deal/${encodeURIComponent(d.deal_id)}`)}
                  className="group cursor-pointer hover:bg-teal-panel/30 transition-colors"
                >
                  <td className="px-4 py-3 font-head font-semibold text-slate-near">
                    {d.deal_name || 'Untitled deal'}
                  </td>
                  <td className="px-4 py-3">
                    <Badge tone={isEFB ? 'taupe' : 'teal'}>
                      {isEFB && <Landmark className="w-3 h-3" />}
                      {d.routing || '—'}
                    </Badge>
                  </td>
                  <td className="px-4 py-3">
                    <Badge tone={statusTone(d.status)}>{prettyStatus(d.status)}</Badge>
                  </td>
                  <td className="px-4 py-3 tnum text-slate/80">{dealKeyMetric(d)}</td>
                  <td className="px-4 py-3 text-slate/50 whitespace-nowrap">{fmtDate(d.updated_at)}</td>
                  <td className="px-4 py-3">
                    <div
                      className="flex items-center justify-end gap-1 opacity-0 group-hover:opacity-100 transition-opacity"
                      onClick={(e) => e.stopPropagation()}
                    >
                      <button
                        type="button"
                        aria-label={isArchived ? 'Unarchive' : 'Archive'}
                        title={isArchived ? 'Unarchive' : 'Archive'}
                        onClick={() =>
                          onAction(() =>
                            isArchived ? unarchiveDeal(d.deal_id) : archiveDeal(d.deal_id),
                          )
                        }
                        className="p-1.5 rounded-lg text-slate/40 hover:text-teal hover:bg-teal-panel transition-colors"
                      >
                        {isArchived ? (
                          <ArchiveRestore className="w-3.5 h-3.5" />
                        ) : (
                          <Archive className="w-3.5 h-3.5" />
                        )}
                      </button>
                      <button
                        type="button"
                        aria-label="Delete"
                        title="Delete"
                        onClick={() => onDelete(d)}
                        className="p-1.5 rounded-lg text-slate/40 hover:text-danger hover:bg-danger/5 transition-colors"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </Card>
  );
}

// ---------------------------------------------------------------------------
// Kanban board — deals grouped by status. Status columns are NOT drop targets
// (status is engine-derived; dragging must never fake it). ONLY the Archived
// column acts: drag a live card in -> archive; drag an archived card out ->
// unarchive. No generic status PATCH (borrow-list item 6).
// ---------------------------------------------------------------------------

interface KanbanCol {
  key: string;
  label: string;
  match: (status: string) => boolean;
  isArchive: boolean;
}

const KANBAN_COLS: KanbanCol[] = [
  { key: 'draft', label: 'Draft', match: (s) => s === 'draft', isArchive: false },
  {
    key: 'in_progress',
    label: 'In Progress',
    match: (s) =>
      ['submitted', 'routing', 'analyzing', 'synthesizing', 'awaiting_input', 'awaiting_cp1'].includes(s),
    isArchive: false,
  },
  {
    key: 'computed',
    label: 'Computed',
    match: (s) => ['computed', 'populated', 'exported', 'completed'].includes(s),
    isArchive: false,
  },
  {
    key: 'gate_failed',
    label: 'Gate Failed',
    match: (s) => ['gate_failed', 'failed', 'cancelled'].includes(s),
    isArchive: false,
  },
  { key: 'archived', label: 'Archived', match: (s) => s === 'archived', isArchive: true },
];

function KanbanBoard({
  deals,
  onChanged,
  onError,
  onDelete,
  onAction,
}: {
  deals: DealListItem[];
  onChanged: () => void;
  onError: (msg: string) => void;
  onDelete: (d: DealListItem) => void;
  onAction: (fn: () => Promise<unknown>) => void;
}) {
  const [drag, setDrag] = useState<DealListItem | null>(null);
  const [overCol, setOverCol] = useState<string | null>(null);

  const canDropOn = (col: KanbanCol): boolean =>
    !!drag && (col.isArchive ? drag.status !== 'archived' : drag.status === 'archived');

  const drop = (col: KanbanCol) => {
    if (!drag || !canDropOn(col)) return;
    const d = drag;
    onAction(() => (col.isArchive ? archiveDeal(d.deal_id) : unarchiveDeal(d.deal_id)));
    setDrag(null);
    setOverCol(null);
  };

  return (
    <div>
      <p className="text-xs text-slate/45 mb-3">
        Status is set by the engine, so status columns aren&rsquo;t drop targets. Drag a card into{' '}
        <span className="font-semibold text-slate/60">Archived</span> to shelve it, or back out to
        restore it.
      </p>
      <div className="flex gap-3 overflow-x-auto pb-2">
        {KANBAN_COLS.map((col) => {
          const colDeals = deals.filter((d) => col.match(d.status));
          const isDropTarget = canDropOn(col);
          const isOver = overCol === col.key && isDropTarget;
          return (
            <div
              key={col.key}
              onDragOver={(e) => {
                if (isDropTarget) {
                  e.preventDefault();
                  setOverCol(col.key);
                }
              }}
              onDragLeave={() => setOverCol((c) => (c === col.key ? null : c))}
              onDrop={() => drop(col)}
              className={`shrink-0 w-72 rounded-xl border p-2 transition-colors ${
                isOver
                  ? 'border-teal bg-teal-panel/50'
                  : col.isArchive
                  ? 'border-dashed border-slate/20 bg-slate/[0.02]'
                  : 'border-slate/10 bg-slate/[0.015]'
              }`}
            >
              <div className="flex items-center justify-between px-2 py-1.5 mb-1">
                <span className="font-label text-xs font-semibold uppercase tracking-wide text-slate/50">
                  {col.label}
                </span>
                <span className="text-xs text-slate/35 tnum">{colDeals.length}</span>
              </div>
              <div className="space-y-2">
                {colDeals.map((d) => (
                  <div
                    key={d.deal_id}
                    draggable
                    onDragStart={(e) => {
                      setDrag(d);
                      e.dataTransfer.effectAllowed = 'move';
                      e.dataTransfer.setData('text/plain', d.deal_id);
                    }}
                    onDragEnd={() => {
                      setDrag(null);
                      setOverCol(null);
                    }}
                    className={`cursor-grab active:cursor-grabbing ${
                      drag?.deal_id === d.deal_id ? 'opacity-40' : ''
                    }`}
                  >
                    <DealCard deal={d} onChanged={onChanged} onError={onError} onDelete={onDelete} />
                  </div>
                ))}
                {colDeals.length === 0 && (
                  <p className="px-2 py-6 text-center text-xs text-slate/30">
                    {col.isArchive ? 'Drop here to archive' : 'Empty'}
                  </p>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
