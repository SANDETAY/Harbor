#!/usr/bin/env node
/**
 * Smoke-check: parse all inline <script> blocks in index.html.
 * Catches syntax errors that freeze boot on the splash screen.
 *
 *   node scripts/check-js-syntax.mjs
 */
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const htmlPath = path.join(root, 'index.html');
const html = fs.readFileSync(htmlPath, 'utf8');

const scripts = [...html.matchAll(/<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/gi)].map((m) => m[1]);
if (!scripts.length) {
  console.error('No inline scripts found in index.html');
  process.exit(1);
}

const combined = scripts.join('\n;\n');
try {
  // Parse only — does not execute
  // eslint-disable-next-line no-new-func
  new Function(combined);
} catch (err) {
  console.error('JS syntax error in index.html inline scripts:');
  console.error(err && err.message ? err.message : err);
  process.exit(1);
}

const build = (html.match(/const HARBOR_BUILD_NUMBER = (\d+);/) || [])[1] || '?';
console.log(`OK · ${scripts.length} script block(s) · build ${build} · ${combined.length} chars`);
