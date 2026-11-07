const { buildSync } = require('esbuild');
const { mkdtempSync, unlinkSync, rmdirSync } = require('node:fs');
const { tmpdir } = require('node:os');
const { join } = require('node:path');
const { spawnSync } = require('node:child_process');
const directory = mkdtempSync(join(tmpdir(), 'dream-mono-release-'));
const output = join(directory, 'test.cjs');
try {
  buildSync({ entryPoints: [join(__dirname, 'monoRelease.test.tsx')], bundle: true,
    platform: 'node', format: 'cjs', jsx: 'automatic', outfile: output });
  const result = spawnSync(process.execPath, ['--test', output], { stdio: 'inherit' });
  process.exitCode = result.status ?? 1;
} finally {
  try { unlinkSync(output); } catch (error) { if (error.code !== 'ENOENT') throw error; }
  rmdirSync(directory);
}
