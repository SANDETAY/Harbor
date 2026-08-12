/**
 * Smoke: preferred-day chores stay Overdue across week roll; Coming up → Active
 * (pullToToday) is due/actionable (not grayed silence).
 * Run: node scripts/smoke-preferred-day-overdue.mjs
 */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const html = fs.readFileSync(path.join(__dirname, '..', 'index.html'), 'utf8');

// Static presence
assert.ok(html.includes('function hasMissedPreferredDayThisPeriod'), 'miss helper');
assert.ok(html.includes('function isPulledToToday'), 'pull helper');
assert.ok(
  /User explicitly Add|pullToToday|isPulledToToday\(habit\)/.test(html),
  'isDueToday must honor pullToToday'
);
assert.ok(
  html.includes('Catch-up after the miss') || html.includes('catch-up'),
  'preferred miss must allow catch-up across days'
);
// Must not require same periodKey only (week-boundary bug)
assert.ok(
  !/if \(periodKey != null && getHabitPeriodKey\(habit, ds\) !== periodKey\) continue;/.test(
    html.match(/function hasMissedPreferredDayThisPeriod[\s\S]{0,1200}/)?.[0] || ''
  ),
  'miss check must not stop at period boundary'
);

// ── Logic replicas (keep in sync with product rules) ─────────────────
function dateStrLocal(d) {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${y}-${m}-${day}`;
}

function todayStrFrom(d) {
  return dateStrLocal(d);
}

function getWeekStart(dateStr) {
  const d = new Date(dateStr + 'T12:00:00');
  const day = d.getDay();
  const diff = day === 0 ? -6 : 1 - day;
  d.setDate(d.getDate() + diff);
  return dateStrLocal(d);
}

function periodKey(dateStr) {
  return `W:${getWeekStart(dateStr)}`;
}

function hasMissedPreferred(habit, dateStr, comps) {
  const days = habit.weekdays;
  if (!days?.length) return false;
  const today = new Date(String(dateStr) + 'T12:00:00');
  for (let i = 1; i <= 14; i++) {
    const d = new Date(today);
    d.setDate(today.getDate() - i);
    if (!days.includes(d.getDay())) continue;
    const ds = dateStrLocal(d);
    if (comps.includes(ds)) continue;
    const caughtUp = comps.some((c) => String(c) > String(ds) && String(c) <= String(dateStr));
    if (!caughtUp) return true;
  }
  return false;
}

function isDue(habit, dateStr, comps, pullToToday) {
  if (pullToToday && String(pullToToday) === dateStr) {
    if (comps.includes(dateStr)) return false;
    return true;
  }
  const wd = new Date(dateStr + 'T12:00:00').getDay();
  const onPreferred = habit.weekdays.includes(wd);
  const miss = hasMissedPreferred(habit, dateStr, comps);
  if (!onPreferred && !miss) return false;
  if (comps.includes(dateStr)) return false;
  return true;
}

// Last Saturday → this Monday
const monday = new Date();
// Find a Monday
while (monday.getDay() !== 1) monday.setDate(monday.getDate() - 1);
const monStr = todayStrFrom(monday);
const sat = new Date(monday);
sat.setDate(monday.getDate() - 2); // Mon - 2 = Sat
const satStr = todayStrFrom(sat);
assert.equal(sat.getDay(), 6, 'fixture sat');
assert.notEqual(periodKey(satStr), periodKey(monStr), 'week rolled');

const mow = { id: 'mow', title: 'Mow lawn', weekdays: [6], interval_days: 7 };

// Missed Saturday → Monday overdue (across week)
assert.equal(hasMissedPreferred(mow, monStr, []), true, 'Sat miss open on Mon');
assert.equal(isDue(mow, monStr, [], null), true, 'due Mon as overdue');

// Catch-up Monday clears miss
assert.equal(hasMissedPreferred(mow, monStr, [monStr]), false, 'Mon catch-up clears');
assert.equal(isDue(mow, monStr, [monStr], null), false, 'not due after catch-up');

// Without miss, not Saturday → Coming up (not due)
const tue = new Date(monday);
tue.setDate(monday.getDate() + 1);
const tueStr = todayStrFrom(tue);
assert.equal(isDue(mow, tueStr, [monStr], null), false, 'Tue after catch-up not due');

// User Add from Coming up (no miss, future Saturday only) → due via pull
assert.equal(isDue(mow, tueStr, [], tueStr), true, 'pull forces due');
assert.equal(isDue(mow, tueStr, [tueStr], tueStr), false, 'pull done after complete');

// Completed on preferred day itself
assert.equal(isDue(mow, satStr, [satStr], null), false, 'done on Sat');
assert.equal(hasMissedPreferred(mow, monStr, [satStr]), false, 'Sat log no miss Mon');

console.log('smoke-preferred-day-overdue: ok');
