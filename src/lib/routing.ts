import type { ViewState } from '../types';

// The app uses window.location.hash as its router. Only these hashes are views.
export const VIEWS: readonly ViewState[] = ['dashboard', 'analysis', 'pipeline', 'intake', 'landing'];

// An empty hash opens the landing page.
export const DEFAULT_VIEW: ViewState = 'landing';

// Turn a raw location hash ('#dashboard') into a view, or null when it is not a view.
// Unknown hashes (for example an in-page anchor) must never change the rendered view.
export function viewFromHash(rawHash: string): ViewState | null {
  const hash = rawHash.startsWith('#') ? rawHash.slice(1) : rawHash;
  return (VIEWS as readonly string[]).includes(hash) ? (hash as ViewState) : null;
}
