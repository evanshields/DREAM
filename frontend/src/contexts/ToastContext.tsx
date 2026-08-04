import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from 'react';
import { CheckCircle2, AlertTriangle, Info, X } from 'lucide-react';

// ---------------------------------------------------------------------------
// ToastContext — a small queued toast system (Phase 5). Powers the undo-delete
// pattern and any transient confirmation. Queue + auto-dismiss countdown +
// hover-to-pause + an action-button slot + dedupe. Wrap the app once in App.tsx.
//
// Undo semantics (the reason onExpire exists): a "Deleted. Undo" toast removes
// the row optimistically and fires the REAL delete only when the countdown
// COMPLETES (onExpire). Clicking the action (Undo) cancels — so undo needs zero
// backend. Dismissing early (the X) commits, exactly like letting it run out.
// ---------------------------------------------------------------------------

export type ToastTone = 'ok' | 'danger' | 'info';

export interface ToastAction {
  label: string;
  onClick: () => void;
}

export interface ToastOptions {
  message: string;
  tone?: ToastTone;
  /** Action button (e.g. "Undo"). Clicking it cancels the countdown WITHOUT firing onExpire. */
  action?: ToastAction;
  /** Auto-dismiss window in ms (default 6000). Hovering the toast pauses it. */
  duration?: number;
  /** Fires when the countdown COMPLETES or the toast is dismissed early — but NOT when the
   *  action is clicked. This is where the deferred delete commits. */
  onExpire?: () => void;
  /** Collapse duplicates: a new toast with a dedupeKey already on screen replaces it (resets
   *  the countdown) instead of stacking. */
  dedupeKey?: string;
}

interface ToastRecord extends ToastOptions {
  id: number;
  duration: number;
}

interface ToastContextValue {
  showToast: (opts: ToastOptions) => number;
  dismissToast: (id: number) => void;
}

const ToastContext = createContext<ToastContextValue | null>(null);

export function useToast(): ToastContextValue {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error('useToast must be used within a <ToastProvider>');
  return ctx;
}

let _seq = 1;

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<ToastRecord[]>([]);
  // onExpire is stashed per-toast so dismiss can fire it exactly once (removeToast owns that).
  const firedExpire = useRef<Set<number>>(new Set());

  const removeToast = useCallback((id: number, runExpire: boolean) => {
    setToasts((prev) => {
      const t = prev.find((x) => x.id === id);
      if (t && runExpire && t.onExpire && !firedExpire.current.has(id)) {
        firedExpire.current.add(id);
        // defer so we never call a parent setState synchronously inside this setState updater
        queueMicrotask(() => t.onExpire?.());
      }
      firedExpire.current.delete(id);
      return prev.filter((x) => x.id !== id);
    });
  }, []);

  const showToast = useCallback((opts: ToastOptions): number => {
    const id = _seq++;
    const rec: ToastRecord = { id, duration: opts.duration ?? 6000, ...opts };
    setToasts((prev) => {
      // dedupe: replace an on-screen toast sharing the dedupeKey (commit its pending expire first)
      let next = prev;
      if (opts.dedupeKey) {
        const dupe = prev.find((x) => x.dedupeKey === opts.dedupeKey);
        if (dupe) {
          if (dupe.onExpire && !firedExpire.current.has(dupe.id)) {
            firedExpire.current.add(dupe.id);
            queueMicrotask(() => dupe.onExpire?.());
          }
          firedExpire.current.delete(dupe.id);
          next = prev.filter((x) => x.dedupeKey !== opts.dedupeKey);
        }
      }
      return [...next, rec];
    });
    return id;
  }, []);

  // dismissToast (X or programmatic): commits onExpire, same as letting the countdown finish.
  const dismissToast = useCallback((id: number) => removeToast(id, true), [removeToast]);

  const value = useMemo<ToastContextValue>(() => ({ showToast, dismissToast }), [
    showToast,
    dismissToast,
  ]);

  return (
    <ToastContext.Provider value={value}>
      {children}
      <ToastViewport
        toasts={toasts}
        onExpireToast={(id) => removeToast(id, true)}
        onActionToast={(id, action) => {
          action.onClick();
          removeToast(id, false); // action cancels the pending expire (the undo path)
        }}
        onDismissToast={(id) => removeToast(id, true)}
      />
    </ToastContext.Provider>
  );
}

const TONE_STYLE: Record<ToastTone, { bar: string; icon: typeof Info; iconClass: string }> = {
  ok: { bar: 'bg-ok', icon: CheckCircle2, iconClass: 'text-ok' },
  danger: { bar: 'bg-danger', icon: AlertTriangle, iconClass: 'text-danger' },
  info: { bar: 'bg-teal', icon: Info, iconClass: 'text-teal' },
};

function ToastViewport({
  toasts,
  onExpireToast,
  onActionToast,
  onDismissToast,
}: {
  toasts: ToastRecord[];
  onExpireToast: (id: number) => void;
  onActionToast: (id: number, action: ToastAction) => void;
  onDismissToast: (id: number) => void;
}) {
  if (toasts.length === 0) return null;
  return (
    <div
      className="fixed bottom-5 right-5 z-50 flex flex-col gap-2 w-[min(22rem,calc(100vw-2.5rem))]"
      role="region"
      aria-label="Notifications"
    >
      {toasts.map((t) => (
        <ToastCard
          key={t.id}
          toast={t}
          onExpire={() => onExpireToast(t.id)}
          onAction={() => t.action && onActionToast(t.id, t.action)}
          onDismiss={() => onDismissToast(t.id)}
        />
      ))}
    </div>
  );
}

function ToastCard({
  toast,
  onExpire,
  onAction,
  onDismiss,
}: {
  toast: ToastRecord;
  onExpire: () => void;
  onAction: () => void;
  onDismiss: () => void;
}) {
  const { message, tone = 'info', action, duration } = toast;
  const tstyle = TONE_STYLE[tone];
  const Icon = tstyle.icon;

  const [remaining, setRemaining] = useState(duration);
  const [paused, setPaused] = useState(false);
  const onExpireRef = useRef(onExpire);
  onExpireRef.current = onExpire;

  useEffect(() => {
    if (paused) return;
    if (remaining <= 0) {
      onExpireRef.current();
      return;
    }
    const STEP = 50;
    const t = window.setTimeout(() => setRemaining((r) => Math.max(0, r - STEP)), STEP);
    return () => window.clearTimeout(t);
  }, [remaining, paused]);

  const pct = Math.max(0, Math.min(100, (remaining / duration) * 100));

  return (
    <div
      className="card overflow-hidden shadow-cardHover animate-fade"
      role="status"
      aria-live="polite"
      onMouseEnter={() => setPaused(true)}
      onMouseLeave={() => setPaused(false)}
    >
      <div className="flex items-start gap-3 px-4 py-3">
        <Icon className={`w-4 h-4 mt-0.5 shrink-0 ${tstyle.iconClass}`} aria-hidden />
        <p className="flex-1 text-sm text-slate leading-snug">{message}</p>
        {action && (
          <button
            type="button"
            onClick={onAction}
            className="text-sm font-label font-semibold text-teal hover:text-teal/80 shrink-0"
          >
            {action.label}
          </button>
        )}
        <button
          type="button"
          onClick={onDismiss}
          aria-label="Dismiss"
          className="text-slate/40 hover:text-slate shrink-0"
        >
          <X className="w-3.5 h-3.5" />
        </button>
      </div>
      {/* countdown bar — depletes over `duration`, freezes while hovered */}
      <div className="h-0.5 bg-slate/10">
        <div
          className={`h-full ${tstyle.bar} transition-none`}
          style={{ width: `${pct}%` }}
          aria-hidden
        />
      </div>
    </div>
  );
}
