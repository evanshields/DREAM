import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Search,
  LayoutGrid,
  FilePlus2,
  Landmark,
  CornerDownLeft,
  Building2,
  type LucideIcon,
} from 'lucide-react';
import { listDeals, ApiError, type DealListItem } from '../lib/api';

// ---------------------------------------------------------------------------
// CommandMenu — a global Cmd/Ctrl-K jump palette (Phase 5). Fuzzy jump-to-deal
// (client-side substring match; no library at 2 users) + navigation actions.
// One item shape {label, icon?, to?, onClick?} — presence of `to` means navigate.
// Mounted once in AppShell so it rides every authed page. No side-panel (that is
// Twenty's; a centered modal is right-sized here).
// ---------------------------------------------------------------------------

interface CommandItem {
  id: string;
  label: string;
  hint?: string;
  icon?: LucideIcon;
  to?: string;
  onClick?: () => void;
}

const NAV_ACTIONS: Omit<CommandItem, 'onClick'>[] = [
  { id: 'nav-pipeline', label: 'Go to Pipeline', icon: LayoutGrid, to: '/pipeline' },
  { id: 'nav-underwrite', label: 'New Underwrite', icon: FilePlus2, to: '/underwrite' },
  { id: 'nav-bond', label: 'Bond Screen', icon: Landmark, to: '/bond-screen' },
];

export function CommandMenu() {
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [deals, setDeals] = useState<DealListItem[]>([]);
  const [active, setActive] = useState(0);
  const inputRef = useRef<HTMLInputElement | null>(null);

  // Global hotkey: Cmd/Ctrl-K toggles; Escape closes (handled in the modal too). A custom event
  // lets a UI affordance (the header search button) open the palette without the keyboard.
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && (e.key === 'k' || e.key === 'K')) {
        e.preventDefault();
        setOpen((v) => !v);
      }
    };
    const onOpen = () => setOpen(true);
    document.addEventListener('keydown', onKey);
    window.addEventListener('dream:command-menu', onOpen);
    return () => {
      document.removeEventListener('keydown', onKey);
      window.removeEventListener('dream:command-menu', onOpen);
    };
  }, []);

  // Fetch the deal list once the palette opens (cheap; refreshes each open so new deals show).
  useEffect(() => {
    if (!open) return;
    setQuery('');
    setActive(0);
    let cancelled = false;
    listDeals({ include_archived: true })
      .then((d) => !cancelled && setDeals(d))
      .catch((e) => {
        if (e instanceof ApiError && e.status === 401) return;
        // a failed fetch just means no deal rows — nav actions still work
      });
    // focus after paint
    const t = window.setTimeout(() => inputRef.current?.focus(), 20);
    return () => {
      cancelled = true;
      window.clearTimeout(t);
    };
  }, [open]);

  const close = useCallback(() => setOpen(false), []);

  const items = useMemo<CommandItem[]>(() => {
    const q = query.trim().toLowerCase();
    const nav: CommandItem[] = NAV_ACTIONS.filter(
      (a) => !q || a.label.toLowerCase().includes(q),
    ).map((a) => ({ ...a }));

    const dealItems: CommandItem[] = deals
      .filter((d) => {
        if (!q) return true;
        return (
          (d.deal_name || 'untitled').toLowerCase().includes(q) ||
          d.routing.toLowerCase().includes(q) ||
          d.status.toLowerCase().includes(q)
        );
      })
      .slice(0, 8)
      .map((d) => ({
        id: `deal-${d.deal_id}`,
        label: d.deal_name || 'Untitled deal',
        hint: `${d.routing}${d.status === 'archived' ? ' · archived' : ''}`,
        icon: Building2,
        to: `/deal/${encodeURIComponent(d.deal_id)}`,
      }));

    return [...nav, ...dealItems];
  }, [query, deals]);

  // keep the active index in range as the list shrinks/grows
  useEffect(() => {
    setActive((a) => Math.min(a, Math.max(0, items.length - 1)));
  }, [items.length]);

  const run = useCallback(
    (item: CommandItem | undefined) => {
      if (!item) return;
      close();
      if (item.onClick) item.onClick();
      else if (item.to) navigate(item.to);
    },
    [close, navigate],
  );

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center px-4 pt-[12vh] bg-slate-near/30 backdrop-blur-sm"
      role="dialog"
      aria-modal="true"
      aria-label="Command menu"
      onClick={close}
    >
      <div
        className="w-full max-w-lg card overflow-hidden shadow-cardHover animate-fade"
        onClick={(e) => e.stopPropagation()}
        onKeyDown={(e) => {
          if (e.key === 'Escape') close();
          else if (e.key === 'ArrowDown') {
            e.preventDefault();
            setActive((a) => Math.min(a + 1, items.length - 1));
          } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            setActive((a) => Math.max(a - 1, 0));
          } else if (e.key === 'Enter') {
            e.preventDefault();
            run(items[active]);
          }
        }}
      >
        <div className="flex items-center gap-2 px-4 border-b border-slate/10">
          <Search className="w-4 h-4 text-slate/40 shrink-0" />
          <input
            ref={inputRef}
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              setActive(0);
            }}
            placeholder="Jump to a deal or action…"
            className="w-full py-3.5 text-sm bg-transparent focus:outline-none placeholder:text-slate/40"
          />
          <kbd className="hidden sm:inline text-[10px] font-mono text-slate/40 border border-slate/15 rounded px-1.5 py-0.5">
            ESC
          </kbd>
        </div>

        <ul className="max-h-80 overflow-y-auto py-2">
          {items.length === 0 ? (
            <li className="px-4 py-6 text-center text-sm text-slate/45">No matches.</li>
          ) : (
            items.map((item, i) => {
              const Icon = item.icon;
              const isActive = i === active;
              return (
                <li key={item.id}>
                  <button
                    type="button"
                    onMouseEnter={() => setActive(i)}
                    onClick={() => run(item)}
                    className={`w-full flex items-center gap-3 px-4 py-2.5 text-left text-sm transition-colors ${
                      isActive ? 'bg-teal-panel text-teal' : 'text-slate hover:bg-teal-panel/50'
                    }`}
                  >
                    {Icon && <Icon className="w-4 h-4 shrink-0 opacity-70" />}
                    <span className="flex-1 min-w-0 truncate">{item.label}</span>
                    {item.hint && (
                      <span className="text-[11px] font-label uppercase tracking-wide text-slate/40 shrink-0">
                        {item.hint}
                      </span>
                    )}
                    {isActive && <CornerDownLeft className="w-3.5 h-3.5 text-teal/60 shrink-0" />}
                  </button>
                </li>
              );
            })
          )}
        </ul>
      </div>
    </div>
  );
}
