# Frontend test runner security audit (2026-11-04)

Report only. Nothing was installed and no code, config or lockfile changed. Evidence came from the repo, the npm registry metadata (read with `npm view` and one read-only advisory lookup), and my own background knowledge where marked. GitHub repo pages could not be read from this session, so repo-health items are NOT VERIFIED.

## 1. Bottom line

Install the six-package set below, with hygiene, pinned to exact versions, and review the lockfile diff before merging. No package has an install script, and the registry advisory lookup returned no known advisories for any of the resolved versions. The main cost is footprint: about 82 new packages, mostly from jsdom.

## 2. What the repo has today

- Frontend: `frontend/` (the root `package.json` is a stray `dream-vision-temp` copy with caret ranges and is not the build target).
- Pinned exact in `frontend/package.json`: vite 7.2.4, react and react-dom 19.2.0, TypeScript 5.9.3, @vitejs/plugin-react 5.1.1, @types/react 19.2.5.
- `frontend/package-lock.json`: lockfileVersion 3, 230 package entries, 2 with install scripts (esbuild 0.25.12 and optional fsevents). Both already present today.
- No test runner, no jsdom, no testing-library anywhere (PR 13 evidence, rechecked: zero matches).
- `tsconfig.app.json` includes all of `src`, so test files are type checked by `tsc -b`. `tsconfig.node.json` type checks `vite.config.ts`.
- Local Node is 22.23.4. The Node version on the VPS and in any CI is NOT VERIFIED (no CI config exists in the repo, no `.github` folder).

## 3. Candidate set and exact versions

PR 13 listed five packages. It missed one required peer, so the set is six.

| Package | Pin | Why this version |
|---|---|---|
| vitest | 4.1.12 | Peer range covers vite ^6 or ^7 or ^8, Node ^20 or ^22 or >=24. Tag V4. Matches vite 7.2.4 so vite is not upgraded. |
| jsdom | 30.1.3 | Latest. Needs Node ^22.22.2 or ^24.15 or >=26 (local 22.23.4 passes). |
| @testing-library/react | 16.3.3 | Peers accept React 19 and @types/react 19. |
| @testing-library/dom | 10.4.2 | Required peer of react (^10) and jest-dom (>=10 <11). Missing from PR 13. |
| @testing-library/jest-dom | 7.0.1 | Needs Node >=22. Peer vitest >=0.32. Import path `/vitest`. |
| @testing-library/user-event | 14.6.8 | Zero dependencies. Peer dom >=7.21.4. |

Not chosen: vitest 5.1.0 (current latest, needs Node ^22.12, major version too new to count as reviewed here). vitest 3.2.7 also works with vite 7 but adds about 9 more packages and is the older line. Jest was not evaluated in depth: it needs a Babel or SWC transform layer for TSX and Vite aliases and adds far more packages.

## 4. Per package evidence

All rows below are from registry metadata unless marked.

| Item | vitest | jsdom | RTL | dom | jest-dom | user-event |
|---|---|---|---|---|---|---|
| License | MIT | MIT | MIT | MIT | MIT | MIT |
| Source repo (registry field) | vitest-dev/vitest | jsdom/jsdom | testing-library/react-testing-library | testing-library/dom-testing-library | testing-library/jest-dom | testing-library/user-event |
| First published | 2021-12 | 2011-11 | 2019-05 | 2019-05 | 2019-07 | 2019-06 |
| Pinned version published | 2026-10-15 | 2026-10-15 | 2026-08-27 | 2026-09-13 | 2026-08-09 | 2026-10-13 |
| Versions on registry | 491 | 290 | 123 | 230 | 85 | 207 |
| Published by | GitHub Actions, trusted publisher (OIDC) | GitHub Actions | GitHub Actions | GitHub Actions | GitHub Actions | GitHub Actions |
| Provenance attestation present | yes (SLSA v1) | yes | yes | yes | yes | yes |
| Install scripts (own) | none | none | none | none | none | none |
| Own direct dependencies | 17 listed | 20 | 1 | 8 | 6 | 0 |
| Stars, contributors, security policy, CI | NOT VERIFIED | NOT VERIFIED | NOT VERIFIED | NOT VERIFIED | NOT VERIFIED | NOT VERIFIED |

Maintainers (registry):
- vitest: 5 npm accounts (ariperkkio, antfu, hiogawa, oreanno, yyx990803). The last release was approved by a named human (oreanno) through the trusted publisher flow. Reputation from my own knowledge, not re-checked: Vitest is the Vite team's own recommended runner, run by the Vue and Vite core contributors including Anthony Fu and Evan You.
- jsdom: 6 accounts including domenic (long-time web standards editor, from my own knowledge) and timothygu. 15 years of history.
- Testing Library packages: the same 18 account list on all four, led by kentcdodds and a testing-library-bot account. The org is widely used (from my own knowledge). 18 accounts with publish rights on a shared org is a wide set, so trusted publishing through GitHub Actions matters here.

What provenance does and does not prove: the registry shows an attestation exists and names GitHub Actions as publisher for every pinned version. I did not verify the signatures (that needs `npm audit signatures`, which needs an install tree) and did not confirm the workflow file path matches the repo. Publisher matches repo: NOT VERIFIED beyond the registry fields.

Advisories:
- Registry bulk advisory lookup for all 6 pinned packages plus their 76 other new transitive versions returned an empty result (no advisories) on 2026-11-04.
- Recalled from memory and NOT re-verified: an older Vitest dev server vulnerability (CVE-2025-24964, a remote code execution via a malicious page when the Vitest API server is open) was fixed in 3.0.5 and later, so 4.1.12 is past it. Rule that follows: never run `vitest --api` or the UI on an exposed host.

## 5. Dependency footprint

I resolved the full tree from registry metadata, treating anything the lockfile already satisfies (vite 7.2.4, react 19.2.0, postcss, picomatch 4) as present.

- New package versions added to the lockfile: about 82 (82 resolved for the vitest 4 set, 91 for the vitest 3 set). Lockfile goes from 230 to about 312 entries.
- Packages with install scripts among the new ones, per registry `hasInstallScript`: none. No postinstall, no native build step. jsdom's optional `canvas` peer is NOT installed (optional peer), so no native compile.
- Largest groups: jsdom subtree about 45 packages (css-tree, parse5, undici, whatwg-url, tough-cookie, tldts, @asamuzakjp, @csstools). Vitest about 25 (@vitest/*, chai, tinyexec, magic-string and so on). Testing Library plus helpers about 20.
- Network calls at install or run time: none in install scripts (there are none). At run time jsdom can fetch URLs only if a test asks for it, and vitest opens a local dev server only in UI or API mode. Neither was exercised.
- Individual maintainers of the small transitive packages (for example @exodus/bytes, @asamuzakjp/*, bidi-js, siginfo, stackback) are NOT VERIFIED. Reading each is the part a human reviewer should skim in the lockfile diff.
- Production impact: all six go in `devDependencies`. `vite build` output does not include them, and nothing here runs on the VPS.

## 6. Verdict per package

| Package | Verdict | Condition |
|---|---|---|
| vitest 4.1.12 | Install with hygiene | Exact pin, dev only, never run in API or UI mode on a shared host. |
| jsdom 30.1.3 | Install with hygiene | Exact pin. Confirm dev and CI Node is 22.22.2 or newer first. Biggest subtree, so review the lockfile diff. |
| @testing-library/react 16.3.3 | Install with hygiene | Exact pin. Install together with the dom peer. |
| @testing-library/dom 10.4.2 | Install with hygiene | Exact pin. Required peer. |
| @testing-library/jest-dom 7.0.1 | Install pinned to reviewed version only | Newest major, Node >=22 only. Skippable: the first tests can use plain `expect` instead. |
| @testing-library/user-event 14.6.8 | Install | Zero dependencies. Only needed once click tests start. |

Hygiene means: `npm install -D -E` so no caret ranges, commit `package-lock.json` in the same change, run `npm ci` in review, read the lockfile diff for any package with `hasInstallScript`, `resolved` URLs that are not registry.npmjs.org, or integrity changes to existing entries, and wait for the Evan click before merging.

## 7. Overall recommendation

Approve the six-package set at the exact pins above, as dev dependencies of `frontend/` only, in one reviewed change that touches only `package.json`, `package-lock.json`, `vite.config.ts` and the new test files. Keep the install in a branch with the repo's normal `tsc --noEmit` and `npm run build` gates. If you want the smaller surface first, install vitest, jsdom, react and dom now and add jest-dom and user-event later.

## 8. Minimal setup diff (text only, not applied)

Install command, run by a human after approval:

    cd frontend && npm install -D -E vitest@4.1.12 jsdom@30.1.3 @testing-library/react@16.3.3 @testing-library/dom@10.4.2 @testing-library/jest-dom@7.0.1 @testing-library/user-event@14.6.8

`frontend/package.json`:

    -    "typecheck": "tsc --noEmit"
    +    "typecheck": "tsc --noEmit",
    +    "test": "vitest run"
     ...devDependencies gain, exact, no carets:
    +    "@testing-library/dom": "10.4.2",
    +    "@testing-library/jest-dom": "7.0.1",
    +    "@testing-library/react": "16.3.3",
    +    "@testing-library/user-event": "14.6.8",
    +    "jsdom": "30.1.3",
    +    "vitest": "4.1.12"

`frontend/vite.config.ts` (import changes so the `test` key type checks):

    -import { defineConfig } from 'vite';
    +import { defineConfig } from 'vitest/config';
     ...
    +  test: {
    +    environment: 'jsdom',
    +    setupFiles: ['./src/test/setup.ts'],
    +    include: ['src/**/*.test.{ts,tsx}'],
    +  },

`globals` stays off, so tests import `describe`, `it` and `expect` from `vitest`. This avoids a tsconfig `types` change. It means Testing Library does not auto clean up, so the setup file does it.

`frontend/src/test/setup.ts` (new):

    import '@testing-library/jest-dom/vitest';
    import { cleanup } from '@testing-library/react';
    import { afterEach, vi } from 'vitest';

    afterEach(() => cleanup());

    // No test may reach the network. Tests that need fetch must stub it themselves.
    vi.stubGlobal('fetch', () => {
      throw new Error('fetch is blocked in tests. Stub it in the test.');
    });

## 9. The one test that proves it works

`frontend/src/lib/format.test.tsx` (new). It proves vitest runs TypeScript with the repo's tsconfig, jsdom renders React 19, Testing Library queries work, jest-dom matchers load, and the network guard is on.

    import { render, screen } from '@testing-library/react';
    import { expect, it } from 'vitest';
    import { fmtUSD } from './format';

    it('renders formatted money and blocks the network', () => {
      render(<span data-testid="v">{fmtUSD(1_500_000)}</span>);
      expect(screen.getByTestId('v')).toHaveTextContent('$1.50M');
      expect(() => fetch('/api/anything')).toThrow(/blocked in tests/);
    });

Pass condition: `npm test` prints 1 passed. Then `npx tsc --noEmit` and `npm run build` stay green, and `git diff --stat` shows only the files listed in section 7.

## 10. What I could not verify

- GitHub stars, contributors, release cadence, security policy and CI for all six repos (session had no GitHub read access to them).
- Attestation signatures and workflow identity (needs an install tree).
- Per-maintainer identity for the small transitive packages.
- Node version on the VPS and in any CI.
- That the advisory lookup is complete: it reflects the registry database on 2026-11-04 only.
- Behavior of the full 82 package tree at runtime, since nothing was installed or run.
