// Bundles tests/*.test.ts with esbuild (ships with vite) and runs them with node:test.
import { build } from 'esbuild';
import { readdirSync, mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { spawnSync } from 'node:child_process';

const dir = new URL('../tests/', import.meta.url).pathname;
const entries = readdirSync(dir).filter((f) => f.endsWith('.test.ts')).map((f) => join(dir, f));
const out = mkdtempSync(join(tmpdir(), 'dream-tests-'));
await build({ entryPoints: entries, outdir: out, bundle: true, platform: 'node', format: 'esm', outExtension: { '.js': '.mjs' } });
const files = entries.map((e) => join(out, e.split('/').pop().replace(/\.ts$/, '.mjs')));
process.exit(spawnSync(process.execPath, ['--test', ...files], { stdio: 'inherit' }).status ?? 1);
