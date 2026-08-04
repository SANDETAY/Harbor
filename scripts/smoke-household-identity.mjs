/**
 * Smoke: household person identity + task routing (no browser).
 * Run: node scripts/smoke-household-identity.mjs
 *
 * Covers:
 *  - stable ids (no random hp-* on normalize)
 *  - Fetch does not re-add Brittany/Child when same name/cloud exists
 *  - tag:brittany → Me when identity name keys match
 *  - export prefers user:<uuid> when member linked by name
 */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const html = fs.readFileSync(path.join(__dirname, '..', 'index.html'), 'utf8');

// Extract a contiguous function block from index.html by name (brace-balanced)
function extractFn(src, name) {
  const re = new RegExp(`function ${name}\\s*\\(`);
  const m = re.exec(src);
  if (!m) throw new Error('missing function ' + name);
  let i = m.index;
  // find opening brace of body
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

const FN_NAMES = [
  'normalizeHouseholdPersonNameKey',
  'personNameSlug',
  'stableHouseholdPersonId',
  'portablePersonKey',
  'isWeakHouseholdPersonName',
  'scoreHouseholdProfile',
  'mergeTwoHouseholdProfiles',
  'dedupeHouseholdProfilesList',
  // getMyIdentityNameKeys / nameKeyIsCurrentUser need runtime hooks — test via eval env
];

// Minimal runtime for pure helpers
const HOUSEHOLD_COLOR_PALETTE = ['#4A90A4', '#E8A87C', '#C38D9E', '#41B3A3', '#E27D60'];

const pureSrc = FN_NAMES.map((n) => extractFn(html, n)).join('\n');
const pure = {};
// eslint-disable-next-line no-new-func
const pureFn = new Function(
  'HOUSEHOLD_COLOR_PALETTE',
  `${pureSrc}
  return {
    normalizeHouseholdPersonNameKey,
    personNameSlug,
    stableHouseholdPersonId,
    portablePersonKey,
    isWeakHouseholdPersonName,
    scoreHouseholdProfile,
    mergeTwoHouseholdProfiles,
    dedupeHouseholdProfilesList
  };`
);
Object.assign(pure, pureFn(HOUSEHOLD_COLOR_PALETTE));

// ── stable ids ──────────────────────────────────────────────────
{
  const child = pure.stableHouseholdPersonId({ name: 'Child', role: 'child' });
  assert.equal(child, 'tag-child');
  const same = pure.stableHouseholdPersonId({ id: 'hp-1234567890', name: 'Child' });
  assert.equal(same, 'tag-child', 'legacy hp-* with name Child → tag-child');

  const b = pure.stableHouseholdPersonId({ name: 'Brittany', role: 'spouse' });
  assert.equal(b, 'tag-brittany');

  const uid = 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee';
  const cloud = pure.stableHouseholdPersonId({ cloudUserId: uid, name: 'Brittany' });
  assert.equal(cloud, 'cloud-' + uid.replace(/-/g, '').slice(0, 10));

  const fromPortable = pure.stableHouseholdPersonId({ id: 'user:' + uid, name: 'Brittany' });
  assert.equal(fromPortable, cloud);
}

// ── portable keys ───────────────────────────────────────────────
{
  const uid = '11111111-2222-3333-4444-555555555555';
  assert.equal(
    pure.portablePersonKey({ cloudUserId: uid, name: 'Brittany' }),
    'user:' + uid
  );
  assert.equal(
    pure.portablePersonKey({ name: 'Child', id: 'hp-old' }),
    'tag:child'
  );
}

// ── dedupe: tag-brittany + cloud-xxx same name → one ────────────
{
  const uid = 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee';
  const cloudId = 'cloud-' + uid.replace(/-/g, '').slice(0, 10);
  const list = [
    { id: 'me', name: 'Taylor', role: 'me', color: '#4A90A4', cloudUserId: 'tttttttt-tttt-tttt-tttt-tttttttttttt' },
    { id: 'tag-brittany', name: 'Brittany', role: 'spouse', color: '#E8A87C', cloudUserId: null },
    { id: cloudId, name: 'Brittany', role: 'spouse', color: '#C38D9E', cloudUserId: uid },
    { id: 'tag-child', name: 'Child', role: 'child', color: '#41B3A3', cloudUserId: null },
    { id: 'hp-999', name: 'Child', role: 'child', color: '#E27D60', cloudUserId: null }
  ];
  // Normalize hp to stable first (as ensure does)
  const staged = list.map((p) => ({
    ...p,
    id: pure.stableHouseholdPersonId(p)
  }));
  // Collapse same id
  const byId = new Map();
  staged.forEach((p) => {
    if (byId.has(p.id)) byId.set(p.id, pure.mergeTwoHouseholdProfiles(byId.get(p.id), p));
    else byId.set(p.id, p);
  });
  const { people, idMap } = pure.dedupeHouseholdProfilesList(Array.from(byId.values()));
  const names = people.filter((p) => p.id !== 'me').map((p) => p.name).sort();
  assert.deepEqual(names, ['Brittany', 'Child'], 'one Brittany + one Child after dedupe');
  const brit = people.find((p) => p.name === 'Brittany');
  assert.ok(brit.cloudUserId === uid, 'Brittany keeps cloud link after merge');
  // idMap should remap discarded ids
  assert.ok(Object.keys(idMap).length >= 1 || people.length === 3, 'merged extras');
}

// ── pack collapse simulation: tag + user same person ────────────
{
  const uid = 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb';
  const rows = [
    { id: 'tag:brittany', name: 'Brittany', cloudUserId: null, role: 'spouse' },
    { id: 'user:' + uid, name: 'Brittany', cloudUserId: uid, role: 'member', isSelf: true },
    { id: 'tag:child', name: 'Child', cloudUserId: null, role: 'child' },
    { id: 'tag:child', name: 'Child', cloudUserId: null, role: 'child' }
  ];
  const out = [];
  const nameKey = pure.normalizeHouseholdPersonNameKey;
  const weak = pure.isWeakHouseholdPersonName;
  rows.forEach((row) => {
    const nk = nameKey(row.name);
    const idx = out.findIndex((x) => {
      if (row.cloudUserId && x.cloudUserId && String(row.cloudUserId) === String(x.cloudUserId)) return true;
      if (String(row.id) === String(x.id)) return true;
      if (nk && !weak(row.name) && nameKey(x.name) === nk) return true;
      return false;
    });
    if (idx >= 0) {
      const a = out[idx];
      const b = row;
      const preferB = String(b.id || '').startsWith('user:') && !String(a.id || '').startsWith('user:');
      const base = preferB ? { ...a, ...b } : { ...b, ...a };
      base.cloudUserId = a.cloudUserId || b.cloudUserId || null;
      if (base.cloudUserId) {
        base.id = 'user:' + String(base.cloudUserId);
      }
      out[idx] = base;
    } else out.push({ ...row });
  });
  assert.equal(out.length, 2, 'pack collapses to Brittany + Child');
  assert.ok(out.find((r) => r.cloudUserId === uid), 'Brittany row is user-linked');
}

// ── name identity keys → tag assignee is me ─────────────────────
{
  function nameKeyIsCurrentUser(nameOrSlug, myKeys) {
    const k = pure.normalizeHouseholdPersonNameKey(String(nameOrSlug || '').replace(/-/g, ' '));
    if (!k || k === 'me') return false;
    if (myKeys.has(k) || myKeys.has(k.replace(/\s+/g, ''))) return true;
    const slug = pure.personNameSlug(nameOrSlug);
    return myKeys.has(slug) || myKeys.has(pure.normalizeHouseholdPersonNameKey(slug.replace(/-/g, ' ')));
  }
  const myKeys = new Set(['brittany']);
  assert.equal(nameKeyIsCurrentUser('Brittany', myKeys), true);
  assert.equal(nameKeyIsCurrentUser('brittany', myKeys), true);
  assert.equal(nameKeyIsCurrentUser('tag-brittany'.replace(/^tag-/, ''), myKeys), true);
  assert.equal(nameKeyIsCurrentUser('Taylor', myKeys), false);
  assert.equal(nameKeyIsCurrentUser('Child', myKeys), false);
}

// ── habitAssignedToCurrentUser simulation ───────────────────────
{
  const myId = 'cccccccc-cccc-cccc-cccc-cccccccccccc';
  const myKeys = new Set(['brittany']);
  function assigned(habit) {
    const ids = Array.isArray(habit.personIds) ? habit.personIds : [habit.personId || 'me'];
    if (ids.includes('me')) return true;
    if (ids.some((id) => String(id) === 'user:' + myId)) return true;
    if (ids.some((id) => {
      const sid = String(id || '');
      if (sid.startsWith('tag:')) {
        const slug = sid.slice(4);
        const k = pure.normalizeHouseholdPersonNameKey(slug.replace(/-/g, ' '));
        return myKeys.has(k);
      }
      if (sid.startsWith('tag-')) {
        const k = pure.normalizeHouseholdPersonNameKey(sid.slice(4).replace(/-/g, ' '));
        return myKeys.has(k);
      }
      return false;
    })) return true;
    if (Array.isArray(habit.personRefNames)) {
      if (habit.personRefNames.some((n) => myKeys.has(pure.normalizeHouseholdPersonNameKey(n)))) return true;
    }
    return false;
  }
  assert.equal(assigned({ personIds: ['me'] }), true);
  assert.equal(assigned({ personIds: ['user:' + myId] }), true);
  assert.equal(assigned({ personIds: ['tag:brittany'], personRefNames: ['Brittany'] }), true);
  assert.equal(assigned({ personIds: ['tag-brittany'] }), true);
  assert.equal(assigned({ personIds: ['tag:taylor'] }), false);
  assert.equal(assigned({ personIds: ['tag:child'], personRefNames: ['Child'] }), false);
}

// ── source guards: apply profiles before habits ─────────────────
{
  const applyIdx = html.indexOf('function applyHouseholdLifePack');
  const applyChunk = html.slice(applyIdx, applyIdx + 14000);
  const profilesMarker = applyChunk.indexOf('People FIRST');
  const habitsMarker = applyChunk.indexOf('if (Array.isArray(payload.habits))');
  assert.ok(profilesMarker > 0, 'apply has People FIRST comment');
  assert.ok(habitsMarker > profilesMarker, 'profiles block before habits in applyHouseholdLifePack');
  assert.ok(applyChunk.includes('deletedProfileKeys'), 'apply merges people-tag tombstones');
}

// ── source guards: export uses personNameSlug ───────────────────
{
  const exp = extractFn(html, 'exportPersonRef');
  assert.ok(exp.includes('personNameSlug'), 'exportPersonRef uses stable slug helper');
  assert.ok(exp.includes('user:'), 'exportPersonRef can emit user: refs');
}

// ── source guards: profile delete tombstones + assignee safety ──
{
  assert.ok(html.includes('function recordDeletedHouseholdProfile'), 'profile delete records tombstone');
  assert.ok(html.includes('function isProfileTombstoned'), 'profile tombstone matcher exists');
  assert.ok(html.includes('deletedProfileKeys'), 'life share carries deletedProfileKeys');
  const imp = extractFn(html, 'importHabitFromShare');
  assert.ok(imp.includes('onlyAmbiguousSelfRefs'), 'import only rewrites legacy me→author');
  assert.ok(imp.includes('intentionallyForMe'), 'import keeps explicit assignee as Me');
  assert.ok(imp.includes('refIsAmbiguousSelf'), 'import does not use author name as hint for tag refs');
}

// ── import safety simulation: tagged Brittany stays Me ──────────
{
  const brittanyId = 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb';
  const taylorId = 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa';
  function refIsAmbiguousSelf(ref) {
    const r = String(ref || '').trim();
    return !r || r === 'me' || r === 'tag:me-local' || r === 'tag:me';
  }
  function refExplicitlyTargetsMe(ref, nameHint, myId, myKeys) {
    const r = String(ref || '');
    if (myId && r.startsWith('user:') && String(r.slice(5)) === String(myId)) return true;
    const check = (n) => {
      const k = pure.normalizeHouseholdPersonNameKey(String(n || '').replace(/-/g, ' '));
      return k && (myKeys.has(k) || myKeys.has(k.replace(/\s+/g, '')));
    };
    if (nameHint && check(nameHint)) return true;
    if (r.startsWith('tag:') && check(r.slice(4))) return true;
    if (r.startsWith('tag-') && check(r.slice(4))) return true;
    return false;
  }
  function shouldRewriteToAuthor(refs, names, myId, authorId, myKeys) {
    const intentionallyForMe = refs.some((ref, i) =>
      refExplicitlyTargetsMe(ref, names[i] || null, myId, myKeys)
    );
    const onlyAmbiguousSelfRefs = refs.length > 0 && refs.every(refIsAmbiguousSelf);
    const idsAllMe = true; // after correct importPersonRef for Brittany
    return idsAllMe && authorId !== myId && onlyAmbiguousSelfRefs && !intentionallyForMe;
  }
  const myKeys = new Set(['brittany']);
  // Family task: Taylor tagged Brittany
  assert.equal(
    shouldRewriteToAuthor(
      ['user:' + brittanyId],
      ['Brittany'],
      brittanyId,
      taylorId,
      myKeys
    ),
    false,
    'explicit user:brittany must NOT become Taylor'
  );
  assert.equal(
    shouldRewriteToAuthor(
      ['tag:brittany'],
      ['Brittany'],
      brittanyId,
      taylorId,
      myKeys
    ),
    false,
    'tag:brittany must NOT become Taylor'
  );
  // Legacy partner Me-only task still says me
  assert.equal(
    shouldRewriteToAuthor(
      ['me'],
      [],
      brittanyId,
      taylorId,
      myKeys
    ),
    true,
    'ambiguous me from partner still maps to author'
  );
}

// ── profile tombstone keys for Adeline ──────────────────────────
{
  const person = { id: 'tag-adeline', name: 'Adeline', role: 'child', cloudUserId: null };
  const keys = new Set();
  keys.add(pure.portablePersonKey(person));
  keys.add(pure.stableHouseholdPersonId(person));
  keys.add(pure.personNameSlug(person.name));
  keys.add('tag:' + pure.personNameSlug(person.name));
  assert.ok(keys.has('tag:adeline'), 'portable tag:adeline');
  assert.ok(keys.has('tag-adeline'), 'stable tag-adeline');
  // Wife’s “Addie” is a different key — not suppressed by Adeline tombstone
  const addieKey = pure.portablePersonKey({ name: 'Addie', role: 'child' });
  assert.equal(addieKey, 'tag:addie');
  assert.ok(!keys.has(addieKey), 'Addie stays independent of Adeline tombstone');
}

console.log('OK · smoke-household-identity · stable ids, dedupe, tag→me, tombstones, import safety');
