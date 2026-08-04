/**
 * Smoke test: dinners modal shell lock / release (anchor + menu freeze bug).
 * Run: node scripts/smoke-dinners-modal-shell.mjs
 *
 * Simulates the class toggle rules without a browser:
 *   body.harbor-modal-open  →  site-root pointer-events none + summary-orb hidden
 */
import assert from 'node:assert/strict';

// ── minimal DOM mock ────────────────────────────────────────────
class FakeEl {
  constructor(tag, attrs = {}) {
    this.tagName = String(tag || 'DIV').toUpperCase();
    this.id = attrs.id || '';
    this.className = attrs.className || '';
    this.children = [];
    this.parent = null;
    this.isConnected = false;
    this.style = { opacity: '1', display: 'block', visibility: 'visible' };
  }
  get classList() {
    const self = this;
    return {
      contains: (c) => self.className.split(/\s+/).includes(c),
      add: (c) => {
        const s = new Set(self.className.split(/\s+/).filter(Boolean));
        s.add(c);
        self.className = [...s].join(' ');
      },
      remove: (c) => {
        self.className = self.className.split(/\s+/).filter(x => x && x !== c).join(' ');
      },
    };
  }
  appendChild(el) {
    el.parent = this;
    el.isConnected = true;
    this.children.push(el);
    return el;
  }
  remove() {
    if (!this.parent) {
      this.isConnected = false;
      return;
    }
    this.parent.children = this.parent.children.filter(c => c !== this);
    this.parent = null;
    this.isConnected = false;
  }
  querySelectorAll() {
    return [];
  }
  contains(el) {
    return this.children.includes(el);
  }
}

const body = new FakeEl('body');
const siteRoot = new FakeEl('div', { id: 'site-root' });
body.appendChild(siteRoot);

globalThis.document = {
  body,
  querySelectorAll(sel) {
    // only support body > .fixed
    if (sel === 'body > .fixed') {
      return body.children.filter(c => c.classList.contains('fixed'));
    }
    return [];
  },
  getElementById(id) {
    return body.children.find(c => c.id === id) || null;
  },
  querySelector(sel) {
    if (sel === 'body > .fixed.inset-0') {
      return body.children.find(c => c.classList.contains('fixed') && c.classList.contains('inset-0')) || null;
    }
    return null;
  },
};

globalThis.window = {
  getComputedStyle(el) {
    return {
      display: el.style.display || 'block',
      visibility: el.style.visibility || 'visible',
      opacity: el.style.opacity ?? '1',
      position: el.classList.contains('fixed') ? 'fixed' : 'static',
    };
  },
};

// ── port of shell helpers (keep in sync with index.html) ─────────
function harborBlockingOverlays(exceptEl) {
  const nodes = document.querySelectorAll('body > .fixed');
  const out = [];
  nodes.forEach(el => {
    if (!el || !el.isConnected) return;
    if (exceptEl && (el === exceptEl || exceptEl.contains?.(el))) return;
    const cls = el.className || '';
    const isFullBleed = /\binset-0\b/.test(cls) || el.classList.contains('inset-0');
    if (!isFullBleed && el.id !== 'summary-modal' && el.id !== 'app-menu-sheet') return;
    try {
      const st = window.getComputedStyle(el);
      if (st.display === 'none' || st.visibility === 'hidden') return;
      const op = parseFloat(st.opacity);
      if (Number.isFinite(op) && op < 0.05 && el.tagName === 'INPUT') return;
    } catch (_) { /* ignore */ }
    out.push(el);
  });
  return out;
}

function acquireHarborModalShell() {
  document.body.classList.add('harbor-modal-open');
}

function releaseHarborModalShell(exceptEl) {
  if (harborBlockingOverlays(exceptEl).length === 0) {
    document.body.classList.remove('harbor-modal-open');
  }
}

function shellLocked() {
  return document.body.classList.contains('harbor-modal-open');
}

function openOverlay(id) {
  const el = new FakeEl('div', {
    id,
    className: 'fixed inset-0 modal-overlay-blur',
  });
  body.appendChild(el);
  acquireHarborModalShell();
  return el;
}

function closeOverlay(el) {
  el.remove();
  releaseHarborModalShell();
}

// ── scenarios ───────────────────────────────────────────────────
let passed = 0;
function check(name, fn) {
  try {
    // reset
    body.children.slice().forEach(c => {
      if (c.id !== 'site-root') c.remove();
    });
    document.body.classList.remove('harbor-modal-open');
    fn();
    console.log('  OK ', name);
    passed++;
  } catch (err) {
    console.error('  FAIL', name, '—', err.message);
    process.exitCode = 1;
  }
}

console.log('Smoke: dinners modal shell (anchor / menu freeze)\n');

check('open dinners locks shell', () => {
  openOverlay('dinners-browser-modal');
  assert.equal(shellLocked(), true);
});

check('close dinners unlocks shell', () => {
  const m = openOverlay('dinners-browser-modal');
  closeOverlay(m);
  assert.equal(shellLocked(), false);
  assert.equal(harborBlockingOverlays().length, 0);
});

check('browser → detail keeps lock (no flash unlock)', () => {
  const browser = openOverlay('dinners-browser-modal');
  browser.remove(); // swap without release
  assert.equal(shellLocked(), true); // still locked even with no overlay until release called
  // Proper swap: remove browser, open detail with acquire
  const detail = openOverlay('dinner-detail-modal');
  assert.equal(shellLocked(), true);
  closeOverlay(detail);
  assert.equal(shellLocked(), false);
});

check('detail → edit → dismiss returns clean (regression)', () => {
  const detail = openOverlay('dinner-detail-modal');
  detail.remove(); // old bug left shell locked with no overlay
  // FIXED path: acquire for edit
  const edit = openOverlay('meal-edit-modal');
  assert.equal(shellLocked(), true);
  // dismiss edit without return (cancel)
  closeOverlay(edit);
  assert.equal(shellLocked(), false, 'shell must unlock when edit dismissed with no return sheet');
});

check('detail → edit → save → dinner detail', () => {
  let detail = openOverlay('dinner-detail-modal');
  detail.remove();
  const edit = openOverlay('meal-edit-modal');
  edit.remove();
  // return to dinners detail
  detail = openOverlay('dinner-detail-modal');
  assert.equal(shellLocked(), true);
  closeOverlay(detail);
  assert.equal(shellLocked(), false);
});

check('ghost opacity file input does not block release', () => {
  const m = openOverlay('dinners-browser-modal');
  const ghost = new FakeEl('input', { className: 'fixed inset-0' });
  ghost.style.opacity = '0.01';
  body.appendChild(ghost);
  m.remove();
  releaseHarborModalShell();
  // ghost is INPUT with low opacity — ignored
  assert.equal(shellLocked(), false);
});

check('stuck shell from bare remove is fixable via releaseHarborModalShell', () => {
  const m = openOverlay('dinners-browser-modal');
  m.remove(); // bug path: no release
  assert.equal(shellLocked(), true);
  releaseHarborModalShell();
  assert.equal(shellLocked(), false);
});

console.log(`\n${passed} checks passed`);
if (process.exitCode) {
  console.error('\nSmoke FAILED');
  process.exit(1);
}
console.log('Smoke OK — shell lock/release behaves correctly\n');
