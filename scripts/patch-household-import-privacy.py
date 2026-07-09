#!/usr/bin/env python3
"""Add household profiles + color-coded events, export/import, and privacy statement."""

from pathlib import Path

path = Path(__file__).resolve().parent.parent / "index.html"
text = path.read_text(encoding="utf-8")
orig = text
n = 0


def replace_once(old: str, new: str, label: str) -> None:
    global text, n
    if old not in text:
        raise SystemExit(f"FAIL: could not find block for {label}")
    text = text.replace(old, new, 1)
    n += 1
    print(f"ok {label}")


# ── 1) CSS for person color badges ──────────────────────────────────────────
CSS_MARKER = """    .app-menu-item i {
      width: 1rem;
      text-align: center;
      color: rgb(var(--harbor-primary-light));
    }"""

CSS_NEW = """    .app-menu-item i {
      width: 1rem;
      text-align: center;
      color: rgb(var(--harbor-primary-light));
    }

    /* Household person color coding on events */
    .person-swatch {
      width: 0.55rem;
      height: 0.55rem;
      border-radius: 999px;
      flex-shrink: 0;
      box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.18);
    }
    .person-swatch--lg {
      width: 0.72rem;
      height: 0.72rem;
    }
    .person-chip {
      display: inline-flex;
      align-items: center;
      gap: 0.28rem;
      padding: 0.12rem 0.45rem 0.12rem 0.28rem;
      border-radius: 999px;
      font-size: 0.58rem;
      font-weight: 650;
      letter-spacing: 0.01em;
      line-height: 1.2;
      max-width: 7.5rem;
      border: 1px solid transparent;
      background: rgba(255, 255, 255, 0.04);
    }
    .person-chip span {
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    .person-pick-grid {
      display: flex;
      flex-wrap: wrap;
      gap: 0.4rem;
    }
    .person-pick-btn {
      display: inline-flex;
      align-items: center;
      gap: 0.35rem;
      padding: 0.4rem 0.65rem;
      border-radius: 999px;
      border: 1px solid rgb(var(--harbor-border));
      background: rgb(var(--harbor-raised));
      color: rgb(var(--harbor-muted));
      font-size: 0.72rem;
      font-weight: 600;
      transition: border-color 0.12s ease, background 0.12s ease, color 0.12s ease;
    }
    .person-pick-btn.is-active {
      color: rgb(var(--harbor-text));
      border-color: var(--person-color, rgb(var(--harbor-primary)));
      background: color-mix(in srgb, var(--person-color, rgb(var(--harbor-primary))) 18%, transparent);
    }
    .cal-event-row--person {
      border-left: 3px solid var(--person-color, rgb(var(--harbor-primary)));
    }
    .summary-timeline-row--person {
      border-left: 3px solid var(--person-color, rgb(var(--harbor-primary)));
      padding-left: 0.45rem;
    }
    .household-profile-row {
      display: flex;
      align-items: center;
      gap: 0.65rem;
      padding: 0.65rem 0.75rem;
      border-radius: 0.9rem;
      border: 1px solid rgb(var(--harbor-border));
      background: rgb(var(--harbor-raised));
    }
    .household-color-dot {
      width: 1.1rem;
      height: 1.1rem;
      border-radius: 999px;
      flex-shrink: 0;
      border: 2px solid rgba(255, 255, 255, 0.2);
      box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.15);
    }
    .privacy-block {
      background: rgb(var(--harbor-raised));
      border: 1px solid rgb(var(--harbor-border));
      border-radius: 1rem;
      padding: 0.85rem 0.95rem;
    }
    .privacy-block h4 {
      font-size: 0.78rem;
      font-weight: 700;
      color: rgb(var(--harbor-text));
      margin-bottom: 0.35rem;
    }
    .privacy-block p {
      font-size: 0.68rem;
      line-height: 1.45;
      color: rgb(var(--harbor-muted));
      margin-bottom: 0.55rem;
    }
    .privacy-block p:last-child {
      margin-bottom: 0;
    }"""

replace_once(CSS_MARKER, CSS_NEW, "css person badges")

# ── 2) Bump build ───────────────────────────────────────────────────────────
replace_once("const HARBOR_BUILD = 'v100';", "const HARBOR_BUILD = 'v101';", "build bump")

# ── 3) Initial state + default state: householdProfiles ─────────────────────
INIT_SETTINGS_TAIL = """        // Privacy: never send calendar feed URLs through third-party CORS proxies unless user opts in
        calendarAllowCorsHelper: false,
        mealPresetsVersion: MEAL_PRESETS_VERSION
      }
    };"""

INIT_SETTINGS_NEW = """        // Privacy: never send calendar feed URLs through third-party CORS proxies unless user opts in
        calendarAllowCorsHelper: false,
        mealPresetsVersion: MEAL_PRESETS_VERSION,
        // Household members for color-coded schedule events (spouse, kids, etc.)
        householdProfiles: [
          { id: 'me', name: 'Me', role: 'me', color: '#2F9B8C' }
        ]
      }
    };"""

replace_once(INIT_SETTINGS_TAIL, INIT_SETTINGS_NEW, "initial state householdProfiles")

DEFAULT_SETTINGS_TAIL = """          cheatDayFundEnabled: true,
          calendarAllowCorsHelper: false,
          mealPresetsVersion: MEAL_PRESETS_VERSION
        }
      };
    }"""

DEFAULT_SETTINGS_NEW = """          cheatDayFundEnabled: true,
          calendarAllowCorsHelper: false,
          mealPresetsVersion: MEAL_PRESETS_VERSION,
          householdProfiles: [
            { id: 'me', name: 'Me', role: 'me', color: '#2F9B8C' }
          ]
        }
      };
    }"""

replace_once(DEFAULT_SETTINGS_TAIL, DEFAULT_SETTINGS_NEW, "default state householdProfiles")

# ── 4) loadState migration ──────────────────────────────────────────────────
LOAD_MIGRATE_MARKER = """      if (!state.settings.importedCalendarEvents) {
        state.settings.importedCalendarEvents = [];
      }"""

LOAD_MIGRATE_NEW = """      if (!state.settings.importedCalendarEvents) {
        state.settings.importedCalendarEvents = [];
      }
      // Ensure household profiles exist and always include a "Me" entry
      state.settings.householdProfiles = ensureHouseholdProfiles(state.settings.householdProfiles);"""

replace_once(LOAD_MIGRATE_MARKER, LOAD_MIGRATE_NEW, "loadState householdProfiles")

# ── 5) Household helpers + export/import + privacy (after getUserProfile) ───
HELPERS_ANCHOR = """    function getCaloriesPerMile(habit, weightKg) {"""

HELPERS_BLOCK = r'''    // ==================== HOUSEHOLD PROFILES ====================
    const HOUSEHOLD_COLOR_PALETTE = [
      '#2F9B8C', // teal (default Me)
      '#A78BFA', // lavender
      '#F97316', // orange
      '#38BDF8', // sky
      '#F472B6', // pink
      '#FACC15', // yellow
      '#34D399', // emerald
      '#FB7185', // rose
      '#818CF8', // indigo
      '#94A3B8'  // slate
    ];

    const HOUSEHOLD_ROLE_OPTIONS = [
      { id: 'me', label: 'Me' },
      { id: 'spouse', label: 'Spouse / partner' },
      { id: 'child', label: 'Child' },
      { id: 'other', label: 'Other' }
    ];

    function defaultHouseholdProfiles() {
      return [{ id: 'me', name: 'Me', role: 'me', color: HOUSEHOLD_COLOR_PALETTE[0] }];
    }

    function ensureHouseholdProfiles(list) {
      const out = [];
      const seen = new Set();
      (Array.isArray(list) ? list : []).forEach((p, i) => {
        if (!p || typeof p !== 'object') return;
        const id = String(p.id || `hp-${i}`).slice(0, 40);
        if (seen.has(id)) return;
        seen.add(id);
        const color = /^#[0-9A-Fa-f]{6}$/.test(p.color || '')
          ? p.color
          : HOUSEHOLD_COLOR_PALETTE[out.length % HOUSEHOLD_COLOR_PALETTE.length];
        const role = ['me', 'spouse', 'child', 'other'].includes(p.role) ? p.role : 'other';
        const name = String(p.name || (role === 'me' ? 'Me' : 'Family')).trim().slice(0, 32) || 'Family';
        out.push({ id, name, role, color });
      });
      if (!out.some(p => p.id === 'me' || p.role === 'me')) {
        out.unshift({ id: 'me', name: 'Me', role: 'me', color: HOUSEHOLD_COLOR_PALETTE[0] });
      }
      // Prefer a single "me" role
      let meSeen = false;
      return out.map(p => {
        if (p.role === 'me' || p.id === 'me') {
          if (meSeen) return { ...p, role: p.role === 'me' ? 'other' : p.role };
          meSeen = true;
          return { ...p, id: p.id || 'me', role: 'me' };
        }
        return p;
      });
    }

    function getHouseholdProfiles() {
      if (!state.settings) state.settings = {};
      state.settings.householdProfiles = ensureHouseholdProfiles(state.settings.householdProfiles);
      return state.settings.householdProfiles;
    }

    function getHouseholdPerson(personId) {
      if (!personId) return null;
      return getHouseholdProfiles().find(p => p.id === personId) || null;
    }

    function getPersonColor(personId) {
      return getHouseholdPerson(personId)?.color || null;
    }

    function getPersonLabel(personId) {
      return getHouseholdPerson(personId)?.name || '';
    }

    function nextHouseholdColor() {
      const used = new Set(getHouseholdProfiles().map(p => (p.color || '').toLowerCase()));
      return HOUSEHOLD_COLOR_PALETTE.find(c => !used.has(c.toLowerCase()))
        || HOUSEHOLD_COLOR_PALETTE[getHouseholdProfiles().length % HOUSEHOLD_COLOR_PALETTE.length];
    }

    function renderPersonChipHtml(personId, options = {}) {
      const person = getHouseholdPerson(personId);
      if (!person) return '';
      const { showName = true, size = 'sm' } = options;
      const sw = size === 'lg' ? 'person-swatch person-swatch--lg' : 'person-swatch';
      if (!showName) {
        return `<span class="${sw}" style="background:${escapeBriefHtml(person.color)}" title="${escapeBriefHtml(person.name)}" aria-label="${escapeBriefHtml(person.name)}"></span>`;
      }
      return `<span class="person-chip" style="border-color:${escapeBriefHtml(person.color)}55;color:${escapeBriefHtml(person.color)}">
        <span class="${sw}" style="background:${escapeBriefHtml(person.color)}"></span>
        <span>${escapeBriefHtml(person.name)}</span>
      </span>`;
    }

    function buildPersonPickerHtml(selectedId) {
      const people = getHouseholdProfiles();
      const sel = selectedId || 'me';      return `<div class="person-pick-grid" id="cal-ev-person-picker" role="group" aria-label="Who is this for?">
        ${people.map(p => {
          const active = p.id === sel;
          return `<button type="button" class="person-pick-btn${active ? ' is-active' : ''}" data-person-id="${escapeBriefHtml(p.id)}"
            style="--person-color:${escapeBriefHtml(p.color)}" aria-pressed="${active ? 'true' : 'false'}">
            <span class="person-swatch" style="background:${escapeBriefHtml(p.color)}"></span>
            ${escapeBriefHtml(p.name)}
          </button>`;
        }).join('')}
      </div>`;
    }

    function wirePersonPicker(modal, initialId) {
      let selected = initialId || 'me';
      const grid = modal.querySelector('#cal-ev-person-picker');
      if (!grid) return () => selected;
      grid.querySelectorAll('.person-pick-btn').forEach(btn => {
        btn.onclick = () => {
          selected = btn.dataset.personId || 'me';
          grid.querySelectorAll('.person-pick-btn').forEach(b => {
            const on = b.dataset.personId === selected;
            b.classList.toggle('is-active', on);
            b.setAttribute('aria-pressed', on ? 'true' : 'false');
          });
        };
      });
      return () => selected;
    }

    function showHouseholdProfilesModal() {
      closeAppMenu();
      const modal = document.createElement('div');
      modal.id = 'household-profiles-modal';
      modal.className = 'fixed inset-0 bg-harbor-bg/70 modal-overlay-blur flex items-end z-[62]';

      const paint = () => {
        const people = getHouseholdProfiles();
        const listEl = modal.querySelector('#household-list');
        if (!listEl) return;
        listEl.innerHTML = people.map(p => {
          const roleLabel = HOUSEHOLD_ROLE_OPTIONS.find(r => r.id === p.role)?.label || p.role;
          const isMe = p.role === 'me' || p.id === 'me';
          return `
            <div class="household-profile-row" data-person-id="${escapeBriefHtml(p.id)}">
              <span class="household-color-dot" style="background:${escapeBriefHtml(p.color)}"></span>
              <div class="flex-1 min-w-0">
                <div class="text-sm font-semibold text-harbor-text truncate">${escapeBriefHtml(p.name)}</div>
                <div class="text-[10px] text-harbor-muted">${escapeBriefHtml(roleLabel)}</div>
              </div>
              <button type="button" class="hp-edit text-[10px] font-semibold text-harbor-primary-light px-2 py-1">Edit</button>
              ${isMe ? '' : '<button type="button" class="hp-del text-harbor-muted hover:text-rose-400 text-sm px-1" aria-label="Remove">×</button>'}
            </div>`;
        }).join('') || '<div class="text-xs text-harbor-muted">No household profiles yet.</div>';

        listEl.querySelectorAll('.household-profile-row').forEach(row => {
          const id = row.dataset.personId;
          row.querySelector('.hp-edit')?.addEventListener('click', () => openHouseholdPersonEditor(id, paint));
          row.querySelector('.hp-del')?.addEventListener('click', () => {
            const person = getHouseholdPerson(id);
            if (!person || person.role === 'me' || person.id === 'me') return;
            if (!confirm(`Remove ${person.name} from household profiles? Events stay, but lose this color label.`)) return;
            state.settings.householdProfiles = getHouseholdProfiles().filter(p => p.id !== id);
            // Clear personId on events that pointed here → fall back to me visually only when missing
            const clearPerson = (list) => (list || []).map(e => e.personId === id ? { ...e, personId: null } : e);
            if (state.settings.mockCalendar?.events) {
              state.settings.mockCalendar.events = clearPerson(state.settings.mockCalendar.events);
            }
            if (state.settings.importedCalendarEvents) {
              state.settings.importedCalendarEvents = clearPerson(state.settings.importedCalendarEvents);
            }
            saveState();
            paint();
            renderSchedule();
            renderTodayFeed();
            showToast(`${person.name} removed`);
          });
        });
      };

      modal.innerHTML = `
        <div class="absolute inset-0" onclick="this.closest('.fixed').remove()"></div>
        <div onclick="event.stopImmediatePropagation()" class="modal-sheet relative w-full bg-harbor-surface border-t border-harbor-border rounded-t-3xl p-5 text-sm max-h-[88vh] overflow-y-auto">
          <div class="modal-grab-pill" aria-hidden="true"></div>
          <div class="font-semibold text-lg mb-1 flex items-center justify-between">
            <span>Household</span>
            <button type="button" onclick="this.closest('.fixed').remove()" class="text-harbor-muted text-2xl leading-none">×</button>
          </div>
          <div class="text-[11px] text-harbor-muted mb-4 leading-snug">
            Add a spouse, partner, or child and pick a color. Tag events so Summary and Schedule show who each plan is for.
          </div>
          <div id="household-list" class="space-y-2 mb-4"></div>
          <button type="button" id="household-add-btn"
            class="w-full py-3 rounded-2xl bg-harbor-primary text-white font-semibold active:opacity-90 mb-2">
            <i class="fa-solid fa-plus mr-1.5"></i>Add person
          </button>
          <button type="button" onclick="this.closest('.fixed').remove()"
            class="w-full py-3 rounded-2xl bg-harbor-raised border border-harbor-border text-harbor-muted font-semibold">Done</button>
        </div>`;
      document.body.appendChild(modal);
      paint();
      modal.querySelector('#household-add-btn').onclick = () => openHouseholdPersonEditor(null, paint);
    }

    function openHouseholdPersonEditor(personId, onDone) {
      const existing = personId ? getHouseholdPerson(personId) : null;
      const isMe = existing && (existing.role === 'me' || existing.id === 'me');
      const draft = existing
        ? { ...existing }
        : { id: 'hp-' + Date.now(), name: '', role: 'spouse', color: nextHouseholdColor() };

      const editor = document.createElement('div');
      editor.className = 'fixed inset-0 bg-harbor-bg/70 modal-overlay-blur flex items-end z-[70]';
      editor.innerHTML = `
        <div class="absolute inset-0" onclick="this.closest('.fixed').remove()"></div>
        <div onclick="event.stopImmediatePropagation()" class="modal-sheet relative w-full bg-harbor-surface border-t border-harbor-border rounded-t-3xl p-5 text-sm">
          <div class="modal-grab-pill" aria-hidden="true"></div>
          <div class="font-semibold text-lg mb-3">${existing ? 'Edit person' : 'Add person'}</div>
          <label class="block text-[10px] text-harbor-muted mb-1">Name</label>
          <input id="hp-name" type="text" maxlength="32" value="${escapeBriefHtml(draft.name)}" placeholder="e.g. Alex, Maya"
            class="w-full bg-harbor-raised border border-harbor-border rounded-2xl px-3 py-2.5 mb-3 text-harbor-text">
          <label class="block text-[10px] text-harbor-muted mb-1">Relationship</label>
          <select id="hp-role" class="w-full bg-harbor-raised border border-harbor-border rounded-2xl px-3 py-2.5 mb-3 text-harbor-text" ${isMe ? 'disabled' : ''}>
            ${HOUSEHOLD_ROLE_OPTIONS.filter(r => isMe ? true : r.id !== 'me').map(r =>
              `<option value="${r.id}" ${draft.role === r.id ? 'selected' : ''}>${r.label}</option>`
            ).join('')}
          </select>
          <label class="block text-[10px] text-harbor-muted mb-1.5">Color</label>
          <div class="flex flex-wrap gap-2 mb-4" id="hp-colors">
            ${HOUSEHOLD_COLOR_PALETTE.map(c => `
              <button type="button" data-color="${c}"
                class="household-color-dot ${draft.color.toLowerCase() === c.toLowerCase() ? 'ring-2 ring-white/80 scale-110' : ''}"
                style="background:${c}; width:1.45rem; height:1.45rem;" aria-label="Color ${c}"></button>
            `).join('')}
          </div>
          <div class="flex gap-2">
            <button type="button" onclick="this.closest('.fixed').remove()"
              class="flex-1 py-3 rounded-2xl bg-harbor-raised border border-harbor-border text-harbor-muted font-semibold">Cancel</button>
            <button type="button" id="hp-save"
              class="flex-1 py-3 rounded-2xl bg-harbor-primary text-white font-semibold">Save</button>
          </div>
        </div>`;
      document.body.appendChild(editor);

      let color = draft.color;
      editor.querySelectorAll('#hp-colors button').forEach(btn => {
        btn.onclick = () => {
          color = btn.dataset.color;
          editor.querySelectorAll('#hp-colors button').forEach(b => {
            b.classList.toggle('ring-2', b.dataset.color === color);
            b.classList.toggle('ring-white/80', b.dataset.color === color);
            b.classList.toggle('scale-110', b.dataset.color === color);
          });
        };
      });

      editor.querySelector('#hp-save').onclick = () => {
        const name = (editor.querySelector('#hp-name')?.value || '').trim().slice(0, 32);
        if (!name) {
          showToast('Enter a name', 'warn');
          editor.querySelector('#hp-name')?.focus();
          return;
        }
        let role = editor.querySelector('#hp-role')?.value || 'other';
        if (isMe) role = 'me';
        if (!['me', 'spouse', 'child', 'other'].includes(role)) role = 'other';
        const people = getHouseholdProfiles().slice();
        const idx = people.findIndex(p => p.id === draft.id);
        const next = { id: draft.id, name, role, color };
        if (idx >= 0) people[idx] = next;
        else people.push(next);
        state.settings.householdProfiles = ensureHouseholdProfiles(people);
        saveState();
        editor.remove();
        if (typeof onDone === 'function') onDone();
        renderSchedule();
        renderTodayFeed();
        showToast(`${name} saved`);
      };
      editor.querySelector('#hp-name')?.focus();
    }

    // ==================== PROFILE EXPORT / IMPORT ====================
    function buildHarborExportPayload() {
      return {
        format: 'harbor-profile',
        version: 1,
        exportedAt: new Date().toISOString(),
        app: 'Harbor',
        build: typeof HARBOR_BUILD !== 'undefined' ? HARBOR_BUILD : null,
        state: JSON.parse(JSON.stringify(state))
      };
    }

    function exportHarborProfile() {
      try {
        const payload = buildHarborExportPayload();
        const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        const day = todayStr();
        const nameHint = (getUserProfile().displayName || 'harbor').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '') || 'harbor';
        a.href = url;
        a.download = `${nameHint}-profile-${day}.json`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        setTimeout(() => URL.revokeObjectURL(url), 1500);
        showToast('Profile exported — share the file with your spouse');
      } catch (err) {
        console.warn('[Harbor] export failed', err);
        showToast('Could not export profile', 'warn');
      }
    }

    function triggerHarborProfileImport() {
      const input = document.createElement('input');
      input.type = 'file';
      input.accept = 'application/json,.json';
      input.style.display = 'none';
      input.onchange = async () => {
        const file = input.files && input.files[0];
        input.remove();
        if (!file) return;
        try {
          const text = await file.text();
          const data = JSON.parse(text);
          showImportProfileModal(data);
        } catch (err) {
          console.warn('[Harbor] import parse failed', err);
          showToast('Invalid Harbor profile file', 'warn');
        }
      };
      document.body.appendChild(input);
      input.click();
    }

    function extractImportState(data) {
      if (!data || typeof data !== 'object') return null;
      // Full Harbor export wrapper
      if (data.format === 'harbor-profile' && data.state && typeof data.state === 'object') {
        return data.state;
      }
      // Raw state blob (legacy / manual)
      if (data.settings || data.habits || data.bills) {
        return data;
      }
      return null;
    }

    function mergeHouseholdProfilesFromImport(incoming) {
      const local = getHouseholdProfiles().slice();
      const byId = new Map(local.map(p => [p.id, p]));
      const byName = new Map(local.map(p => [p.name.toLowerCase(), p]));
      const idMap = {}; // foreignId -> localId
      (Array.isArray(incoming) ? incoming : []).forEach(p => {
        if (!p || !p.id) return;
        if (byId.has(p.id)) {
          idMap[p.id] = p.id;
          return;
        }
        const nameKey = String(p.name || '').toLowerCase();
        if (nameKey && byName.has(nameKey)) {
          idMap[p.id] = byName.get(nameKey).id;
          return;
        }
        // New person — keep id if free, else mint
        let id = String(p.id).slice(0, 40);
        if (byId.has(id)) id = 'hp-' + Date.now() + '-' + Math.random().toString(36).slice(2, 6);
        const role = p.role === 'me' ? 'other' : (['spouse', 'child', 'other'].includes(p.role) ? p.role : 'other');
        const color = /^#[0-9A-Fa-f]{6}$/.test(p.color || '') ? p.color : nextHouseholdColor();
        const entry = {
          id,
          name: String(p.name || 'Family').trim().slice(0, 32) || 'Family',
          role,
          color
        };
        local.push(entry);
        byId.set(id, entry);
        byName.set(entry.name.toLowerCase(), entry);
        idMap[p.id] = id;
      });
      state.settings.householdProfiles = ensureHouseholdProfiles(local);
      return idMap;
    }

    function mergeCalendarEventsFromImport(incomingEvents, personIdMap) {
      const existing = getAllCalendarEvents();
      const existingKeys = new Set(
        existing.map(e => `${getEventDate(e)}|${e.time || ''}|${(e.title || '').toLowerCase()}`)
      );
      const existingIds = new Set(existing.map(e => e.id).filter(Boolean));
      let added = 0;
      const toAdd = [];
      (incomingEvents || []).forEach((e, i) => {
        if (!e || !e.title) return;
        const key = `${getEventDate(e)}|${e.time || ''}|${(e.title || '').toLowerCase()}`;
        if (existingKeys.has(key)) return;
        let id = e.id || getStableCalendarEventId(e, i);
        if (existingIds.has(id)) id = 'ev-import-' + Date.now() + '-' + i;
        let personId = e.personId || null;
        if (personId && personIdMap[personId]) personId = personIdMap[personId];
        if (personId && !getHouseholdPerson(personId)) personId = null;
        toAdd.push({
          ...e,
          id,
          personId,
          date: getEventDate(e),
          durationMin: e.durationMin || 30
        });
        existingKeys.add(key);
        existingIds.add(id);
        added += 1;
      });
      if (toAdd.length) {
        if (!state.settings.mockCalendar) {
          state.settings.mockCalendar = { events: [], freeMinutes: 0, note: '', weekAhead: [] };
        }
        state.settings.mockCalendar.events = normalizeCalendarEvents([
          ...(state.settings.mockCalendar.events || []),
          ...toAdd
        ]).sort((a, b) => `${a.date} ${a.time}`.localeCompare(`${b.date} ${b.time}`));
      }
      return added;
    }

    function applyFullImportReplace(incomingState) {
      const defaults = getDefaultState();
      const next = { ...defaults, ...incomingState };
      next.settings = { ...defaults.settings, ...(incomingState.settings || {}) };
      // Keep local onboarding / theme preferences sane
      next.settings.householdProfiles = ensureHouseholdProfiles(next.settings.householdProfiles);
      if (!Array.isArray(next.habits)) next.habits = [];
      if (!next.completions) next.completions = {};
      state = next;
      persistCalendarEventIds();
      saveState();
    }

    function showImportProfileModal(rawData) {
      const incoming = extractImportState(rawData);
      if (!incoming) {
        showToast('Not a Harbor profile export', 'warn');
        return;
      }
      const inSettings = incoming.settings || {};
      const inEvents = [
        ...((inSettings.mockCalendar && inSettings.mockCalendar.events) || []),
        ...(inSettings.importedCalendarEvents || [])
      ];
      const inPeople = inSettings.householdProfiles || [];
      const habitN = (incoming.habits || []).length;
      const billN = (incoming.bills || []).length;

      const modal = document.createElement('div');
      modal.className = 'fixed inset-0 bg-harbor-bg/70 modal-overlay-blur flex items-end z-[65]';
      modal.innerHTML = `
        <div class="absolute inset-0" onclick="this.closest('.fixed').remove()"></div>
        <div onclick="event.stopImmediatePropagation()" class="modal-sheet relative w-full bg-harbor-surface border-t border-harbor-border rounded-t-3xl p-5 text-sm max-h-[88vh] overflow-y-auto">
          <div class="modal-grab-pill" aria-hidden="true"></div>
          <div class="font-semibold text-lg mb-1 flex items-center justify-between">
            <span>Import profile</span>
            <button type="button" onclick="this.closest('.fixed').remove()" class="text-harbor-muted text-2xl leading-none">×</button>
          </div>
          <div class="text-[11px] text-harbor-muted mb-3 leading-snug">
            Share schedule with a spouse so both apps line up. Import stays on this device only.
          </div>
          <div class="privacy-block mb-4">
            <p><strong class="text-harbor-text">In this file:</strong>
              ${inEvents.length} event${inEvents.length === 1 ? '' : 's'} ·
              ${inPeople.length} household profile${inPeople.length === 1 ? '' : 's'} ·
              ${habitN} task${habitN === 1 ? '' : 's'} ·
              ${billN} bill${billN === 1 ? '' : 's'}
            </p>
          </div>
          <div class="space-y-2 mb-4">
            <button type="button" id="import-mode-merge"
              class="w-full text-left px-3.5 py-3 rounded-2xl border border-harbor-primary/50 bg-harbor-primary/10 active:bg-harbor-primary/20">
              <div class="text-sm font-semibold text-harbor-text">Merge schedule &amp; household</div>
              <div class="text-[10px] text-harbor-muted mt-0.5 leading-snug">Recommended for couples. Adds missing people and events; keeps your tasks, bills, and streaks.</div>
            </button>
            <button type="button" id="import-mode-replace"
              class="w-full text-left px-3.5 py-3 rounded-2xl border border-rose-500/35 bg-rose-950/20 active:bg-rose-900/30">
              <div class="text-sm font-semibold text-rose-200">Replace everything</div>
              <div class="text-[10px] text-harbor-muted mt-0.5 leading-snug">Overwrites this device with the imported profile. Cannot be undone.</div>
            </button>
          </div>
          <button type="button" onclick="this.closest('.fixed').remove()"
            class="w-full py-3 rounded-2xl bg-harbor-raised border border-harbor-border text-harbor-muted font-semibold">Cancel</button>
        </div>`;
      document.body.appendChild(modal);

      modal.querySelector('#import-mode-merge').onclick = () => {
        const personMap = mergeHouseholdProfilesFromImport(inPeople);
        const added = mergeCalendarEventsFromImport(inEvents, personMap);
        refreshCalendarCache();
        saveState();
        modal.remove();
        renderSchedule();
        renderTodayFeed();
        updateSmartBanner();
        showToast(`Merged ${added} event${added === 1 ? '' : 's'} · household updated`);
      };

      modal.querySelector('#import-mode-replace').onclick = () => {
        if (!confirm(
          'Replace ALL data on this device with the imported profile?\n\n' +
          'Tasks, bills, grocery, streaks, and settings will be overwritten. This cannot be undone.'
        )) return;
        applyFullImportReplace(incoming);
        modal.remove();
        showToast('Profile replaced — reloading…');
        setTimeout(() => location.reload(), 450);
      };
    }

    // ==================== PRIVACY STATEMENT ====================
    function showPrivacyStatement() {
      closeAppMenu();
      const modal = document.createElement('div');
      modal.className = 'fixed inset-0 bg-harbor-bg/70 modal-overlay-blur flex items-end z-[62]';
      modal.innerHTML = `
        <div class="absolute inset-0" onclick="this.closest('.fixed').remove()"></div>
        <div onclick="event.stopImmediatePropagation()" class="modal-sheet relative w-full bg-harbor-surface border-t border-harbor-border rounded-t-3xl p-5 text-sm max-h-[88vh] overflow-y-auto">
          <div class="modal-grab-pill" aria-hidden="true"></div>
          <div class="font-semibold text-lg mb-1 flex items-center justify-between">
            <span>Privacy</span>
            <button type="button" onclick="this.closest('.fixed').remove()" class="text-harbor-muted text-2xl leading-none">×</button>
          </div>
          <div class="text-[11px] text-harbor-muted mb-4 leading-snug">How Harbor uses your information — short version.</div>

          <div class="space-y-3">
            <div class="privacy-block">
              <h4><i class="fa-solid fa-hard-drive text-harbor-primary-light mr-1.5"></i>Stored on your device</h4>
              <p>Tasks, habits, bills, grocery lists, subscriptions, streaks, household profiles, and calendar events you create or import live in this browser’s local storage. Harbor does not require an account.</p>
            </div>
            <div class="privacy-block">
              <h4><i class="fa-solid fa-cloud text-harbor-primary-light mr-1.5"></i>What may leave your device</h4>
              <p><strong class="text-harbor-text">Weather:</strong> if you enable real location/weather, approximate location is sent to Open-Meteo (or similar) to fetch a forecast. City name in your profile is optional and only used on-device unless you use weather features that need it.</p>
              <p><strong class="text-harbor-text">Calendar feeds:</strong> if you add an iCal URL, Harbor fetches that URL from this device. By default it does not route through public proxies. Turning on “Allow network helper” may send the feed URL through a third-party CORS helper — leave it off for maximum privacy, or use file import instead.</p>
              <p><strong class="text-harbor-text">Feedback:</strong> if you send feedback, the message and optional contact details go to the feedback provider you submit to (configured by the app). Do not include secrets you don’t want shared.</p>
            </div>
            <div class="privacy-block">
              <h4><i class="fa-solid fa-people-arrows text-harbor-primary-light mr-1.5"></i>Sharing with a spouse</h4>
              <p>Export Profile creates a file on your device. You choose how to share it (message, email, AirDrop, etc.). Import only runs when you pick a file. Harbor does not sync profiles to a cloud account in this build.</p>
            </div>
            <div class="privacy-block">
              <h4><i class="fa-solid fa-ban text-harbor-primary-light mr-1.5"></i>What we don’t do</h4>
              <p>No ads, no trackers, no sale of personal data. Prototype builds may log non-identifying errors in the browser console for debugging.</p>
            </div>
            <div class="privacy-block">
              <h4><i class="fa-solid fa-trash-can text-harbor-primary-light mr-1.5"></i>Your control</h4>
              <p>Factory reset clears Harbor data from this browser. Clearing site data in browser settings does the same. You can export a backup anytime before resetting.</p>
            </div>
          </div>

          <button type="button" onclick="this.closest('.fixed').remove()"
            class="w-full mt-5 py-3 rounded-2xl bg-harbor-primary text-white font-semibold">Got it</button>
          <div class="text-[10px] text-center text-harbor-muted mt-3">Harbor ${typeof HARBOR_BUILD !== 'undefined' ? HARBOR_BUILD : ''} · local-first prototype</div>
        </div>`;
      document.body.appendChild(modal);
    }

    function getCaloriesPerMile(habit, weightKg) {'''

replace_once(HELPERS_ANCHOR, HELPERS_BLOCK, "household/export/privacy helpers")

# ── 6) normalizeCalendarEvents preserves personId ───────────────────────────
NORM_OLD = """    function normalizeCalendarEvents(events) {
      return (events || []).map((e, i) => {
        const date = getEventDate(e);
        let endDate = e?.endDate || null;
        if (endDate && endDate < date) endDate = date;
        if (endDate === date) endDate = null;
        return {
          ...e,
          date,
          endDate: endDate || undefined,
          id: getStableCalendarEventId(e, i),
          durationMin: e.durationMin || 30
        };
      });
    }"""

NORM_NEW = """    function normalizeCalendarEvents(events) {
      return (events || []).map((e, i) => {
        const date = getEventDate(e);
        let endDate = e?.endDate || null;
        if (endDate && endDate < date) endDate = date;
        if (endDate === date) endDate = null;
        const personId = e?.personId && getHouseholdPerson(e.personId) ? e.personId : (e?.personId || undefined);
        return {
          ...e,
          date,
          endDate: endDate || undefined,
          id: getStableCalendarEventId(e, i),
          durationMin: e.durationMin || 30,
          personId: personId || undefined
        };
      });
    }"""

replace_once(NORM_OLD, NORM_NEW, "normalize personId")

# ── 7) Event modal: person picker ───────────────────────────────────────────
EVENT_DURATION_SECTION = """          <div class="text-[10px] uppercase tracking-wider text-harbor-muted font-semibold mb-1.5">Duration</div>"""

EVENT_PERSON_SECTION = """          <div class="text-[10px] uppercase tracking-wider text-harbor-muted font-semibold mb-1.5">Who is this for?</div>
          <div class="mb-3" id="cal-ev-person-wrap"></div>
          <div class="text-[10px] text-harbor-muted mb-3 -mt-1.5 leading-snug">
            Color-codes the event in Schedule &amp; Summary.
            <button type="button" class="text-harbor-primary-light font-semibold underline-offset-2" id="cal-ev-manage-household">Manage household</button>
          </div>

          <div class="text-[10px] uppercase tracking-wider text-harbor-muted font-semibold mb-1.5">Duration</div>"""

replace_once(EVENT_DURATION_SECTION, EVENT_PERSON_SECTION, "event modal person UI")

# Wire person picker after append + duration setup — inject before saveCalendarEvent
EVENT_WIRE_ANCHOR = """      const saveCalendarEvent = () => {
        const title = normalizeUserText(modal.querySelector('#cal-ev-title').value);"""

EVENT_WIRE_NEW = """      const personWrap = modal.querySelector('#cal-ev-person-wrap');
      if (personWrap) {
        personWrap.innerHTML = buildPersonPickerHtml(editEvent?.personId || 'me');
      }
      const getSelectedPersonId = wirePersonPicker(modal, editEvent?.personId || 'me');
      modal.querySelector('#cal-ev-manage-household')?.addEventListener('click', (e) => {
        e.preventDefault();
        showHouseholdProfilesModal();
      });

      const saveCalendarEvent = () => {
        const title = normalizeUserText(modal.querySelector('#cal-ev-title').value);"""

replace_once(EVENT_WIRE_ANCHOR, EVENT_WIRE_NEW, "wire person picker")

PAYLOAD_OLD = """        const payload = {
          date: startDate,
          endDate: endDate !== startDate ? endDate : null,
          time,
          title,
          durationMin
        };"""

PAYLOAD_NEW = """        const payload = {
          date: startDate,
          endDate: endDate !== startDate ? endDate : null,
          time,
          title,
          durationMin,
          personId: getSelectedPersonId() || 'me'
        };"""

replace_once(PAYLOAD_OLD, PAYLOAD_NEW, "event payload personId")

# ── 8) Schedule event row color coding ──────────────────────────────────────
ROW_CONTENT_OLD = """      const contentHtml = `
        <div class="cal-event-body flex items-center gap-x-3 flex-1 min-w-0 cursor-pointer">
          <div class="text-sm font-semibold text-harbor-primary-light tabular-nums w-16 flex-shrink-0">${formatScheduleEventTime(ev.time)}</div>
          <div class="flex-1 min-w-0">
            <div class="font-medium">${ev.title}</div>
            ${showDate ? `<div class="text-[10px] text-harbor-muted">${formatEventDateRangeLabel(getEventDate(ev), getEventEndDate(ev))}</div>` : ''}
            ${getEventEndDate(ev) !== getEventDate(ev) ? `<div class="text-[10px] text-harbor-primary-light/90">Multi-day · ${formatEventDateRangeLabel(getEventDate(ev), getEventEndDate(ev))}</div>` : ''}
            ${ev.durationMin ? `<div class="text-xs text-harbor-muted">${ev.durationMin} min</div>` : ''}
          </div>
        </div>
        <div class="row-inline-actions flex items-center gap-1 flex-shrink-0">
          <button type="button" class="cal-edit-btn text-[10px] text-harbor-primary-light font-medium px-1" title="Edit event">Edit</button>
          <button type="button" class="cal-delete-btn text-harbor-muted hover:text-rose-400 text-sm px-1" title="Delete event">×</button>
        </div>
      `;

      row.innerHTML = buildSwipeRowHtml(
        actionsHtml,
        contentHtml,
        'harbor-card bg-harbor-surface border border-harbor-border rounded-2xl px-4 py-3 flex items-center gap-x-3 active:bg-harbor-border/40'
      );"""

ROW_CONTENT_NEW = """      const person = getHouseholdPerson(ev.personId);
      const personColor = person?.color || '';
      const personChip = person ? renderPersonChipHtml(person.id) : '';
      const contentHtml = `
        <div class="cal-event-body flex items-center gap-x-3 flex-1 min-w-0 cursor-pointer">
          <div class="text-sm font-semibold text-harbor-primary-light tabular-nums w-16 flex-shrink-0">${formatScheduleEventTime(ev.time)}</div>
          <div class="flex-1 min-w-0">
            <div class="font-medium flex items-center gap-1.5 flex-wrap">
              ${person ? `<span class="person-swatch person-swatch--lg" style="background:${escapeBriefHtml(person.color)}"></span>` : ''}
              <span>${escapeBriefHtml(ev.title)}</span>
            </div>
            <div class="flex items-center gap-1.5 flex-wrap mt-0.5">
              ${personChip}
              ${showDate ? `<span class="text-[10px] text-harbor-muted">${formatEventDateRangeLabel(getEventDate(ev), getEventEndDate(ev))}</span>` : ''}
              ${getEventEndDate(ev) !== getEventDate(ev) ? `<span class="text-[10px] text-harbor-primary-light/90">Multi-day</span>` : ''}
              ${ev.durationMin ? `<span class="text-xs text-harbor-muted">${ev.durationMin} min</span>` : ''}
            </div>
          </div>
        </div>
        <div class="row-inline-actions flex items-center gap-1 flex-shrink-0">
          <button type="button" class="cal-edit-btn text-[10px] text-harbor-primary-light font-medium px-1" title="Edit event">Edit</button>
          <button type="button" class="cal-delete-btn text-harbor-muted hover:text-rose-400 text-sm px-1" title="Delete event">×</button>
        </div>
      `;

      const cardClass = 'harbor-card bg-harbor-surface border border-harbor-border rounded-2xl px-4 py-3 flex items-center gap-x-3 active:bg-harbor-border/40'
        + (personColor ? ' cal-event-row--person' : '');
      row.innerHTML = buildSwipeRowHtml(
        actionsHtml,
        contentHtml,
        cardClass
      );
      if (personColor) {
        const front = row.querySelector('.swipe-front') || row.querySelector('.cal-event-body')?.parentElement;
        if (front) front.style.setProperty('--person-color', personColor);
        row.style.setProperty('--person-color', personColor);
      }"""

replace_once(ROW_CONTENT_OLD, ROW_CONTENT_NEW, "schedule row person color")

# ── 9) Today feed schedule card ─────────────────────────────────────────────
FEED_CARD_OLD = """    function renderScheduleFeedCard(ev, container) {
      const card = document.createElement('div');
      card.className = 'habit-row bg-harbor-surface border border-harbor-border rounded-2xl px-4 py-2.5 flex items-center gap-x-3';
      card.dataset.feedType = 'schedule';
      card.innerHTML = `
        <div class="text-sm font-semibold text-harbor-primary-light tabular-nums w-12">${ev.time}</div>
        <div class="flex-1 min-w-0">
          <div class="font-medium text-sm">${ev.title}</div>
          ${ev.durationMin ? `<div class="text-xs text-harbor-muted">${ev.durationMin} min</div>` : ''}
        </div>
        <i class="fa-regular fa-calendar text-harbor-muted text-sm"></i>
      `;
      container.appendChild(card);
    }"""

FEED_CARD_NEW = """    function renderScheduleFeedCard(ev, container) {
      const card = document.createElement('div');
      const person = getHouseholdPerson(ev.personId);
      card.className = 'habit-row bg-harbor-surface border border-harbor-border rounded-2xl px-4 py-2.5 flex items-center gap-x-3'
        + (person ? ' cal-event-row--person' : '');
      if (person) card.style.setProperty('--person-color', person.color);
      card.dataset.feedType = 'schedule';
      card.innerHTML = `
        <div class="text-sm font-semibold text-harbor-primary-light tabular-nums w-12">${escapeBriefHtml(ev.time)}</div>
        <div class="flex-1 min-w-0">
          <div class="font-medium text-sm flex items-center gap-1.5">
            ${person ? `<span class="person-swatch" style="background:${escapeBriefHtml(person.color)}"></span>` : ''}
            <span>${escapeBriefHtml(ev.title)}</span>
          </div>
          <div class="flex items-center gap-1.5 mt-0.5">
            ${person ? renderPersonChipHtml(person.id) : ''}
            ${ev.durationMin ? `<span class="text-xs text-harbor-muted">${ev.durationMin} min</span>` : ''}
          </div>
        </div>
        <i class="fa-regular fa-calendar text-harbor-muted text-sm"></i>
      `;
      container.appendChild(card);
    }"""

replace_once(FEED_CARD_OLD, FEED_CARD_NEW, "today feed person color")

# ── 10) Summary schedule panel ──────────────────────────────────────────────
SUMMARY_DAY_OLD = """        body = evs.length
          ? evs.slice(0, 5).map(e => `
              <div class="summary-timeline-row">
                <div class="summary-time">${escapeBriefHtml(e.time || '—')}</div>
                <div class="min-w-0">
                  <div class="summary-time-title">${escapeBriefHtml(e.title)}</div>
                  <div class="summary-time-meta">${e.durationMin || 30} min</div>
                </div>
              </div>`).join('')
          : '<div class="summary-empty">Open calendar — free block for chores or rest.</div>';"""

SUMMARY_DAY_NEW = """        body = evs.length
          ? evs.slice(0, 5).map(e => {
              const person = getHouseholdPerson(e.personId);
              const style = person ? ` style="--person-color:${escapeBriefHtml(person.color)}"` : '';
              const cls = person ? 'summary-timeline-row summary-timeline-row--person' : 'summary-timeline-row';
              return `
              <div class="${cls}"${style}>
                <div class="summary-time">${escapeBriefHtml(e.time || '—')}</div>
                <div class="min-w-0">
                  <div class="summary-time-title flex items-center gap-1.5">
                    ${person ? `<span class="person-swatch" style="background:${escapeBriefHtml(person.color)}"></span>` : ''}
                    <span>${escapeBriefHtml(e.title)}</span>
                  </div>
                  <div class="summary-time-meta flex items-center gap-1.5 flex-wrap">
                    ${person ? renderPersonChipHtml(person.id) : ''}
                    <span>${e.durationMin || 30} min</span>
                  </div>
                </div>
              </div>`;
            }).join('')
          : '<div class="summary-empty">Open calendar — free block for chores or rest.</div>';"""

replace_once(SUMMARY_DAY_OLD, SUMMARY_DAY_NEW, "summary day person color")

SUMMARY_WEEK_OLD = """                ${(day.events || []).slice(0, 3).map(e => `
                  <div class="summary-timeline-row">
                    <div class="summary-time">${escapeBriefHtml(e.time || '—')}</div>
                    <div class="summary-time-title">${escapeBriefHtml(e.title)}</div>
                  </div>`).join('')}"""

SUMMARY_WEEK_NEW = """                ${(day.events || []).slice(0, 3).map(e => {
                  const person = getHouseholdPerson(e.personId);
                  const style = person ? ` style="--person-color:${escapeBriefHtml(person.color)}"` : '';
                  const cls = person ? 'summary-timeline-row summary-timeline-row--person' : 'summary-timeline-row';
                  return `
                  <div class="${cls}"${style}>
                    <div class="summary-time">${escapeBriefHtml(e.time || '—')}</div>
                    <div class="summary-time-title flex items-center gap-1.5 min-w-0">
                      ${person ? `<span class="person-swatch" style="background:${escapeBriefHtml(person.color)}"></span>` : ''}
                      <span class="truncate">${escapeBriefHtml(e.title)}</span>
                    </div>
                  </div>`;
                }).join('')}"""

replace_once(SUMMARY_WEEK_OLD, SUMMARY_WEEK_NEW, "summary week person color")

# ── 11) Menu items (header + mobile) ────────────────────────────────────────
HEADER_MENU_OLD = """                <button type="button" role="menuitem" class="app-menu-item" data-app-menu-action="settings" onclick="runAppMenuAction('settings')">
                  <i class="fa-solid fa-sliders"></i>
                  <span>Settings</span>
                </button>
                <div class="app-menu-divider" role="separator"></div>
                <div class="app-menu-section-label">Crew</div>"""

HEADER_MENU_NEW = """                <button type="button" role="menuitem" class="app-menu-item" data-app-menu-action="settings" onclick="runAppMenuAction('settings')">
                  <i class="fa-solid fa-sliders"></i>
                  <span>Settings</span>
                </button>
                <button type="button" role="menuitem" class="app-menu-item" data-app-menu-action="import-profile" onclick="runAppMenuAction('import-profile')">
                  <i class="fa-solid fa-file-import"></i>
                  <span>Import profile</span>
                </button>
                <button type="button" role="menuitem" class="app-menu-item" data-app-menu-action="privacy" onclick="runAppMenuAction('privacy')">
                  <i class="fa-solid fa-shield-halved"></i>
                  <span>Privacy</span>
                </button>
                <div class="app-menu-divider" role="separator"></div>
                <div class="app-menu-section-label">Crew</div>"""

replace_once(HEADER_MENU_OLD, HEADER_MENU_NEW, "header menu items")

MOBILE_MENU_OLD = """          <button type="button" role="menuitem" class="app-menu-item mb-1" data-app-menu-action="settings" onclick="runAppMenuAction('settings')">
            <i class="fa-solid fa-sliders"></i>
            <span>Settings</span>
          </button>
          <div class="app-menu-divider" role="separator"></div>
          <div class="app-menu-section-label">Crew</div>"""

MOBILE_MENU_NEW = """          <button type="button" role="menuitem" class="app-menu-item mb-1" data-app-menu-action="settings" onclick="runAppMenuAction('settings')">
            <i class="fa-solid fa-sliders"></i>
            <span>Settings</span>
          </button>
          <button type="button" role="menuitem" class="app-menu-item mb-1" data-app-menu-action="import-profile" onclick="runAppMenuAction('import-profile')">
            <i class="fa-solid fa-file-import"></i>
            <span>Import profile</span>
          </button>
          <button type="button" role="menuitem" class="app-menu-item mb-1" data-app-menu-action="privacy" onclick="runAppMenuAction('privacy')">
            <i class="fa-solid fa-shield-halved"></i>
            <span>Privacy</span>
          </button>
          <div class="app-menu-divider" role="separator"></div>
          <div class="app-menu-section-label">Crew</div>"""

replace_once(MOBILE_MENU_OLD, MOBILE_MENU_NEW, "mobile menu items")

RUN_ACTION_OLD = """    function runAppMenuAction(action) {
      closeAppMenu();
      if (action === 'settings') showSettings();
      else if (action === 'profile') showUserProfile();
      else if (action === 'feedback') showFeedbackModal();
      else if (action === 'streakoff') {
        switchTab('streaks');
        setTimeout(() => {
          document.getElementById('streak-off-panel')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
          showToast('Streak-Offs live on the Streaks tab');
        }, 120);
      }
      else if (action === 'tutorial') {
        startAppTutorial();
        showToast('Starting app tour');
      }
    }"""

RUN_ACTION_NEW = """    function runAppMenuAction(action) {
      closeAppMenu();
      if (action === 'settings') showSettings();
      else if (action === 'profile') showUserProfile();
      else if (action === 'feedback') showFeedbackModal();
      else if (action === 'import-profile') triggerHarborProfileImport();
      else if (action === 'export-profile') exportHarborProfile();
      else if (action === 'privacy') showPrivacyStatement();
      else if (action === 'household') showHouseholdProfilesModal();
      else if (action === 'streakoff') {
        switchTab('streaks');
        setTimeout(() => {
          document.getElementById('streak-off-panel')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
          showToast('Streak-Offs live on the Streaks tab');
        }, 120);
      }
      else if (action === 'tutorial') {
        startAppTutorial();
        showToast('Starting app tour');
      }
    }"""

replace_once(RUN_ACTION_OLD, RUN_ACTION_NEW, "runAppMenuAction")

# ── 12) Settings rows: household, export/import, privacy ────────────────────
SETTINGS_PROFILE_ROW = """            <div class="flex items-center justify-between gap-3 py-1">
              <div class="min-w-0">
                <div class="text-sm font-medium text-harbor-text">User Profile</div>
                <div class="text-[10px] text-harbor-muted leading-snug">Name, body metrics, home base</div>
              </div>
              <button type="button" onclick="this.closest('.fixed').remove(); showUserProfile()"
                class="flex-shrink-0 px-3 py-1.5 rounded-xl bg-harbor-raised border border-harbor-border text-xs font-medium text-harbor-primary-light">
                Open
              </button>
            </div>

            <div class="flex items-center justify-between gap-3 py-1">
              <div class="min-w-0">
                <div class="text-sm font-medium text-harbor-text">Send Feedback</div>
                <div class="text-[10px] text-harbor-muted leading-snug">Report bugs or ideas</div>
              </div>
              <button type="button" onclick="this.closest('.fixed').remove(); showFeedbackModal()"
                class="flex-shrink-0 px-3 py-1.5 rounded-xl bg-harbor-raised border border-harbor-border text-xs font-medium text-harbor-primary-light">
                Open
              </button>
            </div>"""

SETTINGS_PROFILE_NEW = """            <div class="flex items-center justify-between gap-3 py-1">
              <div class="min-w-0">
                <div class="text-sm font-medium text-harbor-text">User Profile</div>
                <div class="text-[10px] text-harbor-muted leading-snug">Name, body metrics, home base</div>
              </div>
              <button type="button" onclick="this.closest('.fixed').remove(); showUserProfile()"
                class="flex-shrink-0 px-3 py-1.5 rounded-xl bg-harbor-raised border border-harbor-border text-xs font-medium text-harbor-primary-light">
                Open
              </button>
            </div>

            <div class="flex items-center justify-between gap-3 py-1">
              <div class="min-w-0">
                <div class="text-sm font-medium text-harbor-text">Household</div>
                <div class="text-[10px] text-harbor-muted leading-snug">Spouse, kids &amp; color-coded events</div>
              </div>
              <button type="button" onclick="this.closest('.fixed').remove(); showHouseholdProfilesModal()"
                class="flex-shrink-0 px-3 py-1.5 rounded-xl bg-harbor-raised border border-harbor-border text-xs font-medium text-harbor-primary-light">
                Manage
              </button>
            </div>

            <div class="py-1">
              <div class="text-sm font-medium text-harbor-text mb-0.5">Share profile</div>
              <div class="text-[10px] text-harbor-muted leading-snug mb-2">Export a backup file so a spouse can import it and match schedules.</div>
              <div class="flex gap-2">
                <button type="button" onclick="exportHarborProfile()"
                  class="flex-1 py-2.5 rounded-2xl bg-harbor-raised border border-harbor-border text-xs font-semibold text-harbor-text active:bg-harbor-border">
                  <i class="fa-solid fa-file-export mr-1.5 text-harbor-primary-light"></i>Export
                </button>
                <button type="button" onclick="this.closest('.fixed').remove(); triggerHarborProfileImport()"
                  class="flex-1 py-2.5 rounded-2xl bg-harbor-primary text-white text-xs font-semibold active:opacity-90">
                  <i class="fa-solid fa-file-import mr-1.5"></i>Import
                </button>
              </div>
            </div>

            <div class="flex items-center justify-between gap-3 py-1">
              <div class="min-w-0">
                <div class="text-sm font-medium text-harbor-text">Privacy</div>
                <div class="text-[10px] text-harbor-muted leading-snug">How your data is stored &amp; used</div>
              </div>
              <button type="button" onclick="this.closest('.fixed').remove(); showPrivacyStatement()"
                class="flex-shrink-0 px-3 py-1.5 rounded-xl bg-harbor-raised border border-harbor-border text-xs font-medium text-harbor-primary-light">
                Read
              </button>
            </div>

            <div class="flex items-center justify-between gap-3 py-1">
              <div class="min-w-0">
                <div class="text-sm font-medium text-harbor-text">Send Feedback</div>
                <div class="text-[10px] text-harbor-muted leading-snug">Report bugs or ideas</div>
              </div>
              <button type="button" onclick="this.closest('.fixed').remove(); showFeedbackModal()"
                class="flex-shrink-0 px-3 py-1.5 rounded-xl bg-harbor-raised border border-harbor-border text-xs font-medium text-harbor-primary-light">
                Open
              </button>
            </div>"""

replace_once(SETTINGS_PROFILE_ROW, SETTINGS_PROFILE_NEW, "settings rows")

# ── 13) Expose on window.HARBOR if present ──────────────────────────────────
if "window.HARBOR = {" in text:
    WH_OLD = None
    # optional — skip if pattern too fragile
    pass

if text == orig:
    raise SystemExit("No changes applied")

path.write_text(text, encoding="utf-8")
print(f"\nWROTE {path} ({n} patches, {len(text)} chars)")
