import { type ReactNode, type ButtonHTMLAttributes, type InputHTMLAttributes } from 'react';
import { type LucideIcon } from 'lucide-react';

// ---------------------------------------------------------------------------
// Small brand-styled primitives (Deep Teal / Off-White / Playfair-Josefin-Noto).
// Intentionally lightweight — no component lib, just Tailwind class compositions.
// ---------------------------------------------------------------------------

function cx(...parts: (string | false | null | undefined)[]): string {
  return parts.filter(Boolean).join(' ');
}

export function Card({ children, className }: { children: ReactNode; className?: string }) {
  return <div className={cx('card', className)}>{children}</div>;
}

type ButtonVariant = 'primary' | 'secondary' | 'ghost';
interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  icon?: LucideIcon;
  children?: ReactNode;
}

export function Button({
  variant = 'primary',
  icon: Icon,
  children,
  className,
  ...rest
}: ButtonProps) {
  const variantClass =
    variant === 'primary' ? 'btn-primary' : variant === 'secondary' ? 'btn-secondary' : 'btn-ghost';
  return (
    <button className={cx(variantClass, className)} {...rest}>
      {Icon && <Icon className="w-4 h-4" />}
      {children}
    </button>
  );
}

export function Input({ className, ...rest }: InputHTMLAttributes<HTMLInputElement>) {
  return <input className={cx('input', className)} {...rest} />;
}

type BadgeTone = 'teal' | 'taupe' | 'ok' | 'warn' | 'danger' | 'neutral' | 'electric';
const BADGE_TONES: Record<BadgeTone, string> = {
  teal: 'bg-teal-panel text-teal border border-teal/20',
  taupe: 'bg-taupe/30 text-slate border border-taupe',
  ok: 'bg-ok/10 text-ok border border-ok/30',
  warn: 'bg-warn/10 text-warn border border-warn/30',
  danger: 'bg-danger/10 text-danger border border-danger/30',
  neutral: 'bg-slate/5 text-slate border border-slate/15',
  electric: 'bg-electric/10 text-electric border border-electric/30',
};

export function Badge({
  children,
  tone = 'neutral',
  className,
}: {
  children: ReactNode;
  tone?: BadgeTone;
  className?: string;
}) {
  return (
    <span
      className={cx(
        'inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-[11px] font-label font-semibold uppercase tracking-wide',
        BADGE_TONES[tone],
        className,
      )}
    >
      {children}
    </span>
  );
}

// Map a deal/job status string to a badge tone.
export function statusTone(status: string): BadgeTone {
  switch (status) {
    case 'computed':
    case 'completed':
    case 'awaiting_cp1':
      return 'ok';
    case 'gate_failed':
    case 'failed':
    case 'cancelled':
      return 'danger';
    case 'awaiting_input':
    case 'analyzing':
    case 'synthesizing':
    case 'routing':
    case 'submitted':
      return 'warn';
    case 'exported':
    case 'populated':
      return 'teal';
    default:
      return 'neutral';
  }
}

export function Spinner({ className }: { className?: string }) {
  return (
    <span
      className={cx('inline-block rounded-full border-2 border-teal/30 border-t-teal animate-spin', className)}
      style={{ width: '1em', height: '1em' }}
      aria-hidden
    />
  );
}
