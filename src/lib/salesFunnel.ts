// Pure helpers for the landing page. No JSX and no framework imports, so they run in plain Node tests.

export type Billing = 'monthly' | 'annual';

// Monthly price in dollars per plan. Enterprise is custom priced, so it has no entry.
const PLAN_PRICES = {
  starter: { monthly: 249, annual: 199 },
  professional: { monthly: 625, annual: 499 },
} as const;

export type PricedPlan = keyof typeof PLAN_PRICES;

export function planPrice(plan: PricedPlan, billing: Billing): number {
  return PLAN_PRICES[plan][billing];
}

// Minimal shape of the document used for scrolling, so tests can pass a fake.
interface ScrollableDocument {
  getElementById(id: string): { scrollIntoView(options?: { behavior?: 'smooth' | 'auto' }): void } | null;
}

// Scroll to a section without touching window.location.hash.
// Plain href="#section" anchors rewrite the hash, which is the app's router.
export function scrollToSection(id: string, doc: ScrollableDocument = document): boolean {
  const element = doc.getElementById(id);
  if (!element) return false;
  element.scrollIntoView({ behavior: 'smooth' });
  return true;
}

// Build a mailto link, or null when no valid sales address is configured.
// No address is hard coded: the page shows a disabled button until one is supplied.
export function contactHref(email: string | undefined, subject: string): string | null {
  const address = (email ?? '').trim();
  if (!/^[^\s@?&]+@[^\s@?&]+\.[^\s@?&]+$/.test(address)) return null;
  return `mailto:${address}?subject=${encodeURIComponent(subject)}`;
}

// Shown under the figures and quotes on the preview page.
export const SAMPLE_CONTENT_NOTICE =
  'Illustrative sample figures and quotes for this product preview. They are not customer data.';
