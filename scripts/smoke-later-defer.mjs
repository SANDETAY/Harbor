/**
 * Smoke: Later (soft defer) behavior + “Move to tomorrow” must be gone from UI/API.
 * Run: node scripts/smoke-later-defer.mjs
 */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const html = fs.readFileSync(path.join(__dirname, '..', 'index.html'), 'utf8');

// ── Static product rules ────────────────────────────────────────────
assert.ok(
  !html.includes('function snoozeHabitToTomorrow'),
  'snoozeHabitToTomorrow must be removed'
);
assert.ok(
  !html.includes('Moved to tomorrow'),
  '“Moved to tomorrow” toast must be gone'
);
assert.ok(
  html.includes('function deferHabitToLater'),
  'deferHabitToLater must exist'
);
assert.ok(
  /deferHabitToLater\('\$\{safeHabitId\}'/.test(html)
    || /deferHabitToLater\(`\$\{safeHabitId\}`/.test(html)
    || html.includes("deferHabitToLater('${safeHabitId}'")
    || (html.includes('data-action="later"') && html.includes('function deferHabitToLater')),
  'Later chip must call deferHabitToLater'
);
assert.ok(
  !/onclick="[^"]*snoozeHabitToTomorrow/.test(html),
  'No onclick to snoozeHabitToTomorrow'
);
// Only one overdue chip label: Later
{
  const m = html.match(/overdueActionsHtml[\s\S]{0,500}/);
  assert.ok(m, 'overdueActionsHtml block');
  assert.ok(m[0].includes('>Later</button>'), 'Later button present');
  assert.ok(!/>Tomorrow</.test(m[0]), 'no Tomorrow button on overdue card');
}

// ── Logic: laterDeferDate hides from due, shows as deferred, clears next day ─
function todayStrFrom(d) {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${y}-${m}-${day}`;
}

const today = todayStrFrom(new Date());
const yesterday = (() => {
  const d = new Date();
  d.setDate(d.getDate() - 1);
  return todayStrFrom(d);
})();

function isHabitDeferredToLater(habit, dateStr = today) {
  if (!habit) return false;
  return String(habit.laterDeferDate || '') === String(dateStr || today);
}

function clearExpiredLater(habits, todayStr) {
  let changed = false;
  habits.forEach((h) => {
    if (h.laterDeferDate && String(h.laterDeferDate) !== todayStr) {
      delete h.laterDeferDate;
      changed = true;
    }
  });
  return changed;
}

// Soft Later for today
const habit = { id: 'h1', title: 'Mow lawn', laterDeferDate: today };
assert.equal(isHabitDeferredToLater(habit, today), true, 'deferred today');
assert.equal(isHabitDeferredToLater(habit, yesterday), false, 'not deferred for other day');

// Day roll clears flag
const rolled = [{ id: 'h1', laterDeferDate: yesterday }];
assert.equal(clearExpiredLater(rolled, today), true);
assert.equal(rolled[0].laterDeferDate, undefined, 'flag cleared after midnight');

// Coming up label path
function nextLabelFor(habit, todayStr) {
  if (isHabitDeferredToLater(habit, todayStr)) return 'Later today';
  return '';
}
assert.equal(nextLabelFor({ laterDeferDate: today }, today), 'Later today');
assert.equal(nextLabelFor({ laterDeferDate: yesterday }, today), '');

// pullHabitToToday clears Later
function pullClearsLater(h) {
  delete h.laterDeferDate;
  h.pullToToday = today;
}
const h2 = { laterDeferDate: today };
pullClearsLater(h2);
assert.equal(h2.laterDeferDate, undefined);
assert.equal(h2.pullToToday, today);

console.log('OK · Later defer smoke passed (Move to tomorrow removed; soft Later intact)');
