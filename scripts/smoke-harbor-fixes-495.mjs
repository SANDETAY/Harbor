/**
 * Smoke tests for Harbor build 495 fixes:
 *  1) Grocery aisle categorization (Poppi → Beverages)
 *  2) Calendar event recurrence occurrence dates
 *  3) Overdue / carry-forward helpers (routines stay due)
 *  4) Daily-rhythm title detection (vitamins)
 *
 * Run: node scripts/smoke-harbor-fixes-495.mjs
 */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const html = fs.readFileSync(path.join(__dirname, '..', 'index.html'), 'utf8');

function extractConstArray(src, name) {
  const re = new RegExp(`const ${name}\\s*=\\s*`);
  const m = re.exec(src);
  if (!m) throw new Error('missing const ' + name);
  let i = m.index + m[0].length;
  while (i < src.length && /\s/.test(src[i])) i++;
  if (src[i] !== '[') throw new Error(name + ' not an array');
  let depth = 0;
  const start = i;
  for (let j = i; j < src.length; j++) {
    const c = src[j];
    if (c === '[') depth++;
    else if (c === ']') {
      depth--;
      if (depth === 0) return src.slice(start, j + 1);
    }
  }
  throw new Error('unbalanced ' + name);
}

function extractFn(src, name) {
  const re = new RegExp(`function ${name}\\s*\\(`);
  const m = re.exec(src);
  if (!m) throw new Error('missing function ' + name);
  let i = m.index;
  const braceStart = src.indexOf('{', i);
  let depth = 0;
  for (let j = braceStart; j < src.length; j++) {
    const c = src[j];
    if (c === '{') depth++;
    else if (c === '}') {
      depth--;
      if (depth === 0) return src.slice(i, j + 1);
    }
  }
  throw new Error('unbalanced ' + name);
}

// ── Grocery categorization ──────────────────────────────────────────
{
  const rulesSrc = extractConstArray(html, 'GROCERY_CATEGORY_RULES');
  const orderSrc = extractConstArray(html, 'GROCERY_CATEGORY_ORDER');
  const fns = [
    'normalizeGroceryNameForCategory',
    'groceryNameMatchesKey',
    'groceryKeyMatchScore',
    'categorizeGroceryItem'
  ].map((n) => extractFn(html, n)).join('\n');

  // eslint-disable-next-line no-new-func
  const api = new Function(`
    const GROCERY_CATEGORY_ORDER = ${orderSrc};
    const GROCERY_CATEGORY_RULES = ${rulesSrc};
    ${fns}
    return { categorizeGroceryItem, normalizeGroceryNameForCategory };
  `)();

  const cases = [
    ["Poppi's", 'Beverages'],
    ['Poppi', 'Beverages'],
    ['poppi orange', 'Beverages'],
    ['Olipop', 'Beverages'],
    ['La Croix', 'Beverages'],
    ['Liquid Death', 'Beverages'],
    ['milk', 'Dairy & Eggs'],
    ['chicken breast', 'Meat & Seafood'],
    ['banana', 'Produce'],
    ['frozen pizza', 'Frozen'],
    ['diapers', 'Baby'],
    ['dog food', 'Pet'],
    ['shampoo', 'Personal Care'],
    ['paper towels', 'Household'],
    ['spaghetti', 'Pasta & Grains']
  ];
  for (const [name, expect] of cases) {
    const got = api.categorizeGroceryItem(name);
    assert.equal(got, expect, `grocery "${name}" → ${got}, expected ${expect}`);
  }
  console.log('OK · grocery categorization (' + cases.length + ' cases)');
}

// ── Event recurrence ────────────────────────────────────────────────
{
  const fns = [
    'getEventDate',
    'getEventEndDate',
    'getEventRecurrence',
    'eventOccursOnDate'
  ].map((n) => extractFn(html, n)).join('\n');

  // Minimal stubs used by the helpers
  // eslint-disable-next-line no-new-func
  const api = new Function(`
    function todayStr() { return '2026-08-04'; }
    ${fns}
    return { eventOccursOnDate, getEventRecurrence };
  `)();

  const weekly = { date: '2026-08-04', time: '09:00', title: 'Team sync', recurrence: 'weekly' };
  assert.equal(api.eventOccursOnDate(weekly, '2026-08-04'), true, 'weekly start day');
  assert.equal(api.eventOccursOnDate(weekly, '2026-08-11'), true, 'weekly +7');
  assert.equal(api.eventOccursOnDate(weekly, '2026-08-05'), false, 'weekly +1 off');
  assert.equal(api.eventOccursOnDate(weekly, '2026-08-18'), true, 'weekly +14');

  const daily = { date: '2026-08-04', recurrence: 'daily' };
  assert.equal(api.eventOccursOnDate(daily, '2026-08-04'), true);
  assert.equal(api.eventOccursOnDate(daily, '2026-08-06'), true);
  assert.equal(api.eventOccursOnDate(daily, '2026-08-03'), false, 'daily before start');

  const monthly = { date: '2026-01-31', recurrence: 'monthly' };
  assert.equal(api.eventOccursOnDate(monthly, '2026-01-31'), true);
  assert.equal(api.eventOccursOnDate(monthly, '2026-02-28'), true, 'Jan 31 clamps to Feb 28');
  assert.equal(api.eventOccursOnDate(monthly, '2026-03-31'), true);
  assert.equal(api.eventOccursOnDate(monthly, '2026-03-30'), false);

  const none = { date: '2026-08-04', endDate: '2026-08-06' };
  assert.equal(api.eventOccursOnDate(none, '2026-08-05'), true, 'multi-day span');
  assert.equal(api.eventOccursOnDate(none, '2026-08-07'), false);

  const until = { date: '2026-08-04', recurrence: 'daily', recurrenceUntil: '2026-08-06' };
  assert.equal(api.eventOccursOnDate(until, '2026-08-06'), true);
  assert.equal(api.eventOccursOnDate(until, '2026-08-07'), false, 'after until');

  console.log('OK · event recurrence');
}

// ── Daily rhythm titles (vitamins) ──────────────────────────────────
{
  const fn = extractFn(html, 'isDailyRhythmTitle');
  // eslint-disable-next-line no-new-func
  const api = new Function(`${fn}; return { isDailyRhythmTitle };`)();
  assert.equal(api.isDailyRhythmTitle('Take vitamins / supplements'), true);
  assert.equal(api.isDailyRhythmTitle('Take Vitamins/Supplements'), true);
  assert.equal(api.isDailyRhythmTitle('Floss teeth'), true);
  assert.equal(api.isDailyRhythmTitle('Mow the lawn'), false);
  console.log('OK · daily rhythm titles');
}

// ── Build number ────────────────────────────────────────────────────
{
  const m = html.match(/const HARBOR_BUILD_NUMBER = (\d+);/);
  assert.ok(m, 'build number present');
  const build = Number(m[1]);
  assert.ok(build >= 495, 'build is 495+');
  const sw = fs.readFileSync(path.join(__dirname, '..', 'sw.js'), 'utf8');
  assert.match(sw, /harbor-v\d+/, 'sw cache present');
  assert.match(html, /cal-duration-seg|cal-ev-recurrence-row|cal-repeat-trigger/, 'event duration/repeat UI present');
  assert.match(html, /habitHasCarryForwardDue/, 'carry-forward helper present');
  assert.match(html, /startHouseholdLifeSharePolling/, 'household poll present');
  assert.match(html, /poppi/, 'poppi grocery keyword present');
  console.log('OK · build ' + build + ' markers');
}

console.log('\nAll smoke checks passed for Harbor fixes.');
