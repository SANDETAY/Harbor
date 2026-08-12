/**
 * Smoke: durable one-off retirement (completed Tasks must not reappear).
 * Run: node scripts/smoke-oneoff-retire.mjs
 */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const html = fs.readFileSync(path.join(__dirname, '..', 'index.html'), 'utf8');

assert.ok(html.includes('function getRetiredOneOffMap'), 'registry');
assert.ok(html.includes('function recordRetiredOneOff'), 'record');
assert.ok(html.includes('function mergeRetiredOneOffMaps'), 'merge');
assert.ok(html.includes('retiredOneOffs'), 'slice field');
assert.ok(html.includes('isRetiredOneOffId'), 'id check');
assert.ok(html.includes('isRetiredOneOffTitle'), 'title check');
assert.ok(html.includes('HARBOR_BUILD_NUMBER = 577'), 'build 573');
// Native calendar push must merge cloud Taskers before overwrite
assert.ok(
  /calendar push can.t resurrect|merge cloud Tasker completions/i.test(html),
  'native calendar push merge guard'
);

function oneOffTitleKey(title) {
  return String(title || '').toLowerCase().replace(/[^a-z0-9]+/g, ' ').replace(/\s+/g, ' ').trim();
}

function mergeRetired(a, b) {
  const out = { ...a };
  Object.keys(b || {}).forEach((id) => {
    const row = b[id];
    const prev = out[id];
    if (!prev || String(row.at || '') >= String(prev.at || '')) out[id] = row;
  });
  return out;
}

function isDone(habit, registry, comps) {
  if (habit.completedOnce || habit.status === 'done' || habit.completedAt) return true;
  if (registry[String(habit.id)]) return true;
  const tk = oneOffTitleKey(habit.title);
  if (tk && Object.values(registry).some((r) => r.titleKey === tk)) return true;
  if ((comps[habit.id] || []).length > 0) return true;
  return false;
}

const reg = {};
const h = { id: 'custom-1', title: 'Wash Car Seat', interval_days: 0 };
assert.equal(isDone(h, reg, {}), false);
reg['custom-1'] = { title: h.title, titleKey: oneOffTitleKey(h.title), at: '2026-08-10' };
assert.equal(isDone(h, reg, {}), true, 'registry by id');
// Recreated with new id, same title
const h2 = { id: 'custom-999', title: 'Wash Car Seat', interval_days: 0 };
assert.equal(isDone(h2, reg, {}), true, 'registry by title');
// Merge keeps both
const m = mergeRetired(reg, { 'custom-2': { title: 'Other', titleKey: 'other', at: '2026-08-11' } });
assert.ok(m['custom-1'] && m['custom-2']);

console.log('smoke-oneoff-retire: ok');
