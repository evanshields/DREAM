// DREAM wordmark — Playfair "DREAM" + a small teal mark. Pure type, no asset dependency.
export function Wordmark({ className }: { className?: string }) {
  return (
    <span className={`inline-flex items-center gap-2 ${className ?? ''}`}>
      <span
        className="inline-flex items-center justify-center rounded-md bg-teal text-offwhite font-head font-bold"
        style={{ width: '1.6em', height: '1.6em', fontSize: '0.85em' }}
        aria-hidden
      >
        D
      </span>
      <span className="font-head font-bold text-slate-near tracking-tight text-xl leading-none">
        DREAM
      </span>
    </span>
  );
}
