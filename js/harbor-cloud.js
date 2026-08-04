/**
 * Harbor ↔ Supabase client
 * Requires: window.HARBOR_SUPABASE { url, anonKey } and supabase-js (global `supabase`).
 */
(function (global) {
  'use strict';

  function log() {
    if (global.HARBOR_SUPABASE && global.HARBOR_SUPABASE.debug) {
      // eslint-disable-next-line no-console
      console.info.apply(console, ['[Harbor cloud]'].concat([].slice.call(arguments)));
    }
  }

  function normalizeUrl(url) {
    let u = String(url || '').trim();
    // Users sometimes paste REST path — client wants project root only
    u = u.replace(/\/rest\/v1\/?$/i, '').replace(/\/+$/, '');
    return u;
  }

  function isNativeCap() {
    try {
      return !!(global.Capacitor && typeof global.Capacitor.isNativePlatform === 'function'
        && global.Capacitor.isNativePlatform());
    } catch (_) {
      return false;
    }
  }

  const Cloud = {
    client: null,
    session: null,
    user: null,
    _ready: false,
    _initPromise: null,
    _oauthListenerBound: false,
    _oauthInFlight: false,

    configured() {
      const c = global.HARBOR_SUPABASE;
      if (!c || !c.url || !c.anonKey) return false;
      if (String(c.url).includes('YOUR_PROJECT')) return false;
      if (String(c.anonKey).includes('YOUR_')) return false;
      return true;
    },

    async init() {
      if (this._initPromise) return this._initPromise;
      this._initPromise = this._doInit();
      return this._initPromise;
    },

    async _doInit() {
      if (!this.configured()) {
        log('Not configured — add docs/supabase/config.local.js');
        return false;
      }
      const createClient = global.supabase && global.supabase.createClient;
      if (typeof createClient !== 'function') {
        console.warn('[Harbor cloud] supabase-js not loaded (need CDN script)');
        return false;
      }
      const url = normalizeUrl(global.HARBOR_SUPABASE.url);
      const key = String(global.HARBOR_SUPABASE.anonKey).trim();
      this.client = createClient(url, key, {
        auth: {
          persistSession: true,
          autoRefreshToken: true,
          detectSessionInUrl: true,
          flowType: 'pkce',
          storage: global.localStorage
        }
      });
      const { data, error } = await this.client.auth.getSession();
      if (error) console.warn('[Harbor cloud] getSession', error.message);
      this._applySession(data && data.session);
      this.client.auth.onAuthStateChange((_event, session) => {
        this._applySession(session);
      });
      this._bindOAuthReturnListener();
      this._ready = true;
      log('Ready', url, this.user ? this.user.email : '(signed out)');
      return true;
    },

    _applySession(session) {
      this.session = session || null;
      this.user = (session && session.user) || null;
      if (!this.user) {
        global.__harborCloudPro = false;
        return;
      }
      // Best-effort: ensure public.profiles row exists (trigger may be missing on older projects)
      try {
        this.ensureProfile().catch(function (err) {
          log('ensureProfile', err && err.message);
        });
      } catch (_) { /* ignore */ }
    },

    /**
     * Upsert a profiles row for the signed-in user.
     * Auth users live in auth.users; Table Editor → profiles only fills when this
     * (or the handle_new_user trigger) runs.
     */
    async ensureProfile() {
      if (!this.client || !this.isSignedIn()) return false;
      const row = {
        id: this.user.id,
        email: this.getEmail() || this.user.email || null,
        updated_at: new Date().toISOString()
      };
      const { error } = await this.client
        .from('profiles')
        .upsert(row, { onConflict: 'id' });
      if (error) {
        log('ensureProfile failed', error.message);
        return false;
      }
      return true;
    },

    isSignedIn() {
      return !!(this.user && this.user.id);
    },

    getEmail() {
      return (this.user && (this.user.email || this.user.user_metadata && this.user.user_metadata.email)) || '';
    },

    async signUp(email, password) {
      await this.init();
      if (!this.client) throw new Error('Cloud not configured');
      const em = String(email || '').trim().toLowerCase();
      if (!em || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(em)) {
        throw new Error('Enter a valid email address');
      }
      if (!password || String(password).length < 8) {
        throw new Error('Password must be at least 8 characters');
      }
      const { data, error } = await this.client.auth.signUp({ email: em, password });
      if (error) throw this._friendlyAuthError(error, 'signup');
      // Supabase may return a user with empty identities when the email is already registered
      // (anti-enumeration) — treat as "already exists" so we never pretend signup succeeded.
      const identities = data && data.user && data.user.identities;
      if (data && data.user && Array.isArray(identities) && identities.length === 0) {
        throw new Error('An account already exists with this email. Sign in or reset your password.');
      }
      this._applySession(data.session);
      if (data.session) await this.refreshProFromProfile();
      return data;
    },

    async signIn(email, password) {
      await this.init();
      if (!this.client) throw new Error('Cloud not configured');
      const em = String(email || '').trim().toLowerCase();
      if (!em) throw new Error('Enter your email');
      if (!password) throw new Error('Enter your password');
      const { data, error } = await this.client.auth.signInWithPassword({
        email: em,
        password
      });
      if (error) throw this._friendlyAuthError(error, 'signin');
      this._applySession(data.session);
      await this.refreshProFromProfile();
      return data;
    },

    /**
     * Send a password-reset email (industry standard).
     * User must open the link; Supabase then establishes a recovery session.
     */
    async resetPassword(email) {
      await this.init();
      if (!this.client) throw new Error('Cloud not configured');
      const em = String(email || '').trim().toLowerCase();
      if (!em || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(em)) {
        throw new Error('Enter the email for your account');
      }
      const redirectTo = this._oauthRedirectUrl('email') || (global.location && global.location.origin
        ? global.location.origin + '/index.html'
        : undefined);
      const { data, error } = await this.client.auth.resetPasswordForEmail(em, {
        redirectTo
      });
      if (error) throw this._friendlyAuthError(error, 'reset');
      return data;
    },

    /** Map email/password auth errors into clear toasts. */
    _friendlyAuthError(err, mode) {
      const raw = (err && (err.message || err.error_description || err.error || err.msg)) || String(err || 'Auth failed');
      const msg = String(raw);
      const low = msg.toLowerCase();
      if (/already\s*registered|already\s*exists|user\s*already|email.*exist/i.test(msg)
          || low.includes('user_already_exists')) {
        return new Error('An account already exists with this email. Sign in or reset your password.');
      }
      if (/invalid login credentials|invalid_credentials|wrong password|invalid email or password/i.test(msg)) {
        return new Error(mode === 'signin'
          ? 'Wrong email or password. Try again or reset your password.'
          : msg);
      }
      if (/email not confirmed|not confirmed/i.test(msg)) {
        return new Error('Confirm your email first — check your inbox for a link from Harbor.');
      }
      if (/password.*at least|password.*characters|weak password/i.test(msg)) {
        return new Error('Password must be at least 8 characters.');
      }
      if (/rate limit|too many requests|email rate/i.test(msg)) {
        return new Error('Too many attempts — wait a minute and try again.');
      }
      if (err instanceof Error) return err;
      return new Error(msg);
    },

    /**
     * Social login (Supabase Auth providers).
     * Supported: Apple, Google. (Microsoft/Azure account login removed — use email if needed.)
     * Google blocks WKWebView — must open system browser (Capacitor Browser).
     * Apple often works in-WebView; still use Browser for a consistent return path.
     */
    async signInWithOAuth(provider) {
      await this.init();
      if (!this.client) throw new Error('Cloud not configured');
      const p = String(provider || '').toLowerCase();
      if (p === 'azure' || p === 'microsoft' || p === 'outlook') {
        throw new Error('Microsoft sign-in is not available. Use Apple, Google, or email.');
      }
      if (p !== 'google' && p !== 'apple') {
        throw new Error('Unsupported sign-in provider');
      }
      const redirectTo = this._oauthRedirectUrl(p);
      this._oauthInFlight = true;
      log('OAuth start', p, 'redirectTo=', redirectTo);
      try {
        const { data, error } = await this.client.auth.signInWithOAuth({
          provider: p,
          options: {
            redirectTo,
            skipBrowserRedirect: true,
            queryParams: p === 'google' ? { access_type: 'offline', prompt: 'select_account' } : undefined
          }
        });
        if (error) {
          this._oauthInFlight = false;
          throw this._friendlyOAuthError(error, p);
        }
        if (!data || !data.url) {
          this._oauthInFlight = false;
          throw new Error('No OAuth URL returned — enable ' + p + ' in Supabase → Authentication → Providers');
        }
        await this._openOAuthUrl(data.url);
        return data;
      } catch (err) {
        this._oauthInFlight = false;
        throw this._friendlyOAuthError(err, p);
      }
    },

    /** Map provider/Supabase errors into something actionable in a toast. */
    _friendlyOAuthError(err, provider) {
      const raw = (err && (err.message || err.error_description || err.error)) || String(err || 'Sign-in failed');
      const msg = String(raw);
      const low = msg.toLowerCase();
      if (/redirect|redirect_uri|not allowed|disallowed/i.test(msg)) {
        return new Error(
          'Redirect URL not allowed. In Supabase → Authentication → URL configuration add: capacitor://localhost/** and com.sandetay.harbor://**'
        );
      }
      if (/server_error|server error|unexpected_failure|500/i.test(msg) || low === 'server_error') {
        if (provider === 'apple') {
          return new Error(
            'Apple sign-in server error — check Supabase → Providers → Apple (Services ID, Key ID, Team ID, .p8 secret). Secret JWTs expire every 6 months.'
          );
        }
        if (provider === 'google') {
          return new Error(
            'Google sign-in server error — check Supabase → Providers → Google Client ID/secret and Google Cloud redirect = …/auth/v1/callback'
          );
        }
        return new Error('Sign-in server error — check provider settings in Supabase Authentication → Providers');
      }
      if (/provider is not enabled|unsupported provider|validation_failed/i.test(msg)) {
        return new Error('Enable ' + (provider || 'this provider') + ' in Supabase → Authentication → Providers');
      }
      if (/disallowed_useragent|403|webview/i.test(msg)) {
        return new Error((provider || 'Provider') + ' blocks in-app browser — update Harbor (Browser plugin required)');
      }
      if (err instanceof Error) return err;
      return new Error(msg);
    },

    /**
     * Where Supabase should send the user after Google/Apple (or email recovery).
     * Must be listed under Authentication → URL configuration → Redirect URLs.
     *
     * Native: capacitor://localhost is the Capacitor WebView origin and the most
     * reliable allow-list entry. Custom scheme com.sandetay.harbor:// is also registered.
     */
    _oauthRedirectUrl(provider) {
      try {
        if (global.HARBOR_SUPABASE && global.HARBOR_SUPABASE.authRedirectTo) {
          return String(global.HARBOR_SUPABASE.authRedirectTo);
        }
        if (isNativeCap()) {
          // Prefer Capacitor content origin — works for Apple/Google/MS when allow-listed.
          // Fallback custom scheme if configured via authRedirectTo.
          return 'capacitor://localhost';
        }
        let loc = global.location;
        try {
          if (global.top && global.top.location && global.top.location.origin) {
            loc = global.top.location;
          }
        } catch (_) { /* ignore */ }
        if (loc && loc.origin) {
          const path = loc.pathname || '/';
          if (/mobile\.html$/i.test(path) || /dual-preview\.html$/i.test(path)) {
            return loc.origin + '/index.html';
          }
          if (/index\.html$/i.test(path) || path === '/' || path.endsWith('/')) {
            return loc.origin + (path === '/' || path.endsWith('/') ? path : path);
          }
          return loc.origin + path;
        }
      } catch (_) { /* ignore */ }
      return undefined;
    },

    async _openOAuthUrl(url) {
      if (!url) return;
      // Prefer Capacitor Browser (SFSafariViewController) — required for Google
      try {
        const Browser = global.Capacitor && global.Capacitor.Plugins && global.Capacitor.Plugins.Browser;
        if (Browser && typeof Browser.open === 'function') {
          await Browser.open({ url: url, presentationStyle: 'fullscreen' });
          return;
        }
      } catch (err) {
        log('Browser.open failed', err && err.message);
      }
      // Native without Browser plugin: open system Safari via location (may still fail for Google)
      if (isNativeCap()) {
        try {
          global.location.assign(url);
          return;
        } catch (_) { /* ignore */ }
      }
      try {
        const topWin = global.top || global;
        if (topWin && topWin.location) {
          topWin.location.assign(url);
          return;
        }
      } catch (_) { /* ignore */ }
      try {
        const w = global.open(url, '_blank', 'noopener,noreferrer');
        if (!w && global.location) global.location.assign(url);
      } catch (_) {
        if (global.location) global.location.assign(url);
      }
    },

    /** Pull ?code= / #access_token= out of a deep-link or https return URL. */
    _parseOAuthParams(rawUrl) {
      const url = String(rawUrl || '');
      let code = null;
      let access_token = null;
      let refresh_token = null;
      let err = null;
      try {
        // Query string (PKCE): scheme://host/path?code=...
        const qIdx = url.indexOf('?');
        const hIdx = url.indexOf('#');
        let query = '';
        let hash = '';
        if (qIdx !== -1) {
          query = url.slice(qIdx + 1, hIdx !== -1 && hIdx > qIdx ? hIdx : undefined);
        }
        if (hIdx !== -1) {
          hash = url.slice(hIdx + 1);
        }
        if (query) {
          const qp = new URLSearchParams(query);
          code = qp.get('code') || code;
          err = qp.get('error_description') || qp.get('error') || err;
          access_token = qp.get('access_token') || access_token;
          refresh_token = qp.get('refresh_token') || refresh_token;
        }
        if (hash) {
          const hp = new URLSearchParams(hash);
          code = hp.get('code') || code;
          err = hp.get('error_description') || hp.get('error') || err;
          access_token = hp.get('access_token') || access_token;
          refresh_token = hp.get('refresh_token') || refresh_token;
        }
      } catch (_) { /* ignore */ }
      return { code, access_token, refresh_token, err };
    },

    async _closeOAuthBrowser() {
      try {
        const Browser = global.Capacitor && global.Capacitor.Plugins && global.Capacitor.Plugins.Browser;
        if (Browser && Browser.close) await Browser.close();
      } catch (_) { /* ignore */ }
    },

    _notifyOAuthSignedIn() {
      if (typeof global.showToast === 'function') {
        global.showToast('Signed in');
      }
      try {
        if (typeof global.renderTasks === 'function') global.renderTasks();
      } catch (_) { /* ignore */ }
      try {
        // Re-paint Account modal if open
        const paintBtn = global.document && global.document.querySelector('#hc-oauth-apple, #hc-signin');
        if (paintBtn && typeof global.showHarborAccountModal === 'function') {
          /* leave modal; session will show on next open */
        }
      } catch (_) { /* ignore */ }
    },

    /** Handle deep-link / redirect return from OAuth (PKCE code or hash tokens). */
    async handleOAuthReturnUrl(rawUrl) {
      if (!rawUrl) return false;
      if (!this.client) {
        try { await this.init(); } catch (_) { /* ignore */ }
      }
      if (!this.client) return false;
      const url = String(rawUrl);
      if (!/access_token=|refresh_token=|code=|error=|auth\/callback/.test(url)) {
        // Still allow join deep links later; ignore unrelated opens
        return false;
      }
      log('OAuth return', url.slice(0, 160));
      const parsed = this._parseOAuthParams(url);
      if (parsed.err) {
        this._oauthInFlight = false;
        throw new Error(String(parsed.err));
      }
      try {
        // PKCE: exchange auth code (prefer bare code — more reliable than full URL)
        if (parsed.code) {
          const { data, error } = await this.client.auth.exchangeCodeForSession(parsed.code);
          if (error) throw error;
          this._applySession(data && data.session);
          this._oauthInFlight = false;
          await this.refreshProFromProfile();
          await this._closeOAuthBrowser();
          return true;
        }
        // Implicit / hash tokens
        if (parsed.access_token && parsed.refresh_token) {
          const { data, error } = await this.client.auth.setSession({
            access_token: parsed.access_token,
            refresh_token: parsed.refresh_token
          });
          if (error) throw error;
          this._applySession(data && data.session);
          this._oauthInFlight = false;
          await this.refreshProFromProfile();
          await this._closeOAuthBrowser();
          return true;
        }
      } catch (err) {
        console.warn('[Harbor cloud] OAuth return failed', err && err.message);
        this._oauthInFlight = false;
        throw err;
      }
      return false;
    },

    _bindOAuthReturnListener() {
      if (this._oauthListenerBound) return;
      this._oauthListenerBound = true;
      const self = this;
      const onReturn = function (u) {
        if (!u) return;
        // Household join deep link: com.sandetay.harbor://join?code=TOKEN
        try {
          if (/:\/\/join/i.test(u) && typeof global.__harborPendingJoinCode !== 'undefined') {
            /* handled below */
          }
          const joinMatch = u.match(/[?&](?:code|invite)=([A-Fa-f0-9]{32,})/);
          if (/:\/\/join/i.test(u) && joinMatch) {
            global.__harborPendingJoinCode = joinMatch[1];
            if (typeof global.showToast === 'function') {
              global.showToast('Invite code received — open Household to join', 'info');
            }
            return;
          }
        } catch (_) { /* ignore */ }

        self.handleOAuthReturnUrl(u).then(function (ok) {
          if (ok) self._notifyOAuthSignedIn();
        }).catch(function (err) {
          if (typeof global.showToast === 'function') {
            global.showToast((err && err.message) || 'Sign-in return failed', 'warn');
          }
        });
      };

      try {
        const App = global.Capacitor && global.Capacitor.Plugins && global.Capacitor.Plugins.App;
        if (App && typeof App.addListener === 'function') {
          App.addListener('appUrlOpen', function (event) {
            onReturn(event && event.url);
          });
          // Cold start: app opened from deep link
          if (typeof App.getLaunchUrl === 'function') {
            App.getLaunchUrl().then(function (res) {
              if (res && res.url) onReturn(res.url);
            }).catch(function () { /* ignore */ });
          }
        }
      } catch (_) { /* ignore */ }

      // Browser closed — appUrlOpen may race; re-check session after a short delay
      try {
        const Browser = global.Capacitor && global.Capacitor.Plugins && global.Capacitor.Plugins.Browser;
        if (Browser && typeof Browser.addListener === 'function') {
          Browser.addListener('browserFinished', function () {
            setTimeout(function () {
              if (!self.client) return;
              self.client.auth.getSession().then(function (res) {
                const sess = res && res.data && res.data.session;
                if (sess && sess.user) {
                  const was = self.user && self.user.id;
                  self._applySession(sess);
                  if (!was && self._oauthInFlight) {
                    self._oauthInFlight = false;
                    self._notifyOAuthSignedIn();
                  }
                } else if (self._oauthInFlight) {
                  // Deep link may still be processing; wait a bit more before warning
                  setTimeout(function () {
                    if (self._oauthInFlight && !self.isSignedIn()) {
                      self._oauthInFlight = false;
                      if (typeof global.showToast === 'function') {
                        global.showToast(
                          'Sign-in did not finish. Supabase Redirect URLs need: capacitor://localhost/** and com.sandetay.harbor://**',
                          'warn'
                        );
                      }
                    }
                  }, 1500);
                }
              });
            }, 400);
          });
        }
      } catch (_) { /* ignore */ }

      // Web: if we land with hash/query tokens on load
      try {
        if (!isNativeCap() && global.location && /access_token=|code=/.test(String(global.location.href || ''))) {
          self.handleOAuthReturnUrl(global.location.href).then(function (ok) {
            if (ok) self._notifyOAuthSignedIn();
          }).catch(function () { /* ignore */ });
        }
      } catch (_) { /* ignore */ }
    },

    /**
     * Sign out and stay signed out. Clears local session so no cloud backup / household
     * push can run until the user signs in again. Local Harbor data on device is kept.
     */
    async signOut() {
      try {
        await this.init();
      } catch (_) { /* still clear local state */ }
      try {
        if (this.client) {
          // Global revokes refresh token server-side; fall back to local if offline
          try {
            await this.client.auth.signOut({ scope: 'global' });
          } catch (_) {
            await this.client.auth.signOut({ scope: 'local' });
          }
        }
      } catch (err) {
        log('signOut', err && err.message);
      }
      this._clearLocalAuthStorage();
      this._applySession(null);
      global.__harborCloudPro = false;
      this._oauthInFlight = false;
    },

    /** Remove Supabase auth keys from localStorage so session cannot revive after sign-out/reset. */
    _clearLocalAuthStorage() {
      try {
        const keys = [];
        for (let i = 0; i < global.localStorage.length; i++) {
          const k = global.localStorage.key(i);
          if (!k) continue;
          // sb-<project-ref>-auth-token and related
          if (k.startsWith('sb-') && (k.includes('auth') || k.includes('code-verifier'))) {
            keys.push(k);
          }
        }
        keys.forEach((k) => {
          try { global.localStorage.removeItem(k); } catch (_) { /* ignore */ }
        });
      } catch (_) { /* ignore */ }
    },

    async refreshProFromProfile() {
      if (!this.isSignedIn() || !this.client) {
        global.__harborCloudPro = false;
        return false;
      }
      const { data, error } = await this.client
        .from('profiles')
        .select('is_pro, pro_until')
        .eq('id', this.user.id)
        .maybeSingle();
      if (error) {
        log('profile fetch', error.message);
        return false;
      }
      let pro = !!(data && data.is_pro);
      if (data && data.pro_until) {
        const t = new Date(data.pro_until).getTime();
        if (Number.isFinite(t) && t > Date.now()) pro = true;
      }
      global.__harborCloudPro = pro;
      return pro;
    },

    async pushSnapshot(payload, deviceId) {
      await this.init();
      if (!this.isSignedIn()) throw new Error('Sign in to back up to the cloud');
      const row = {
        user_id: this.user.id,
        device_id: deviceId || this._deviceId(),
        schema_version: 1,
        payload: payload,
        updated_at: new Date().toISOString()
      };
      const { data, error } = await this.client
        .from('harbor_snapshots')
        .upsert(row, { onConflict: 'user_id' })
        .select('updated_at')
        .maybeSingle();
      if (error) throw error;
      log('Backup saved', data && data.updated_at);
      return data;
    },

    async pullSnapshot() {
      await this.init();
      if (!this.isSignedIn()) throw new Error('Sign in to restore from the cloud');
      const { data, error } = await this.client
        .from('harbor_snapshots')
        .select('payload, updated_at, device_id')
        .eq('user_id', this.user.id)
        .maybeSingle();
      if (error) throw error;
      if (!data || !data.payload) return null;
      return data;
    },

    _deviceId() {
      try {
        let id = localStorage.getItem('harbor_device_id');
        if (!id) {
          id = 'dev-' + Math.random().toString(36).slice(2, 10) + Date.now().toString(36);
          localStorage.setItem('harbor_device_id', id);
        }
        return id;
      } catch (_) {
        return 'dev-unknown';
      }
    },

    async listMyHouseholds() {
      await this.init();
      if (!this.isSignedIn() || !this.client) return [];
      const { data, error } = await this.client.rpc('list_my_households');
      if (error) throw error;
      return Array.isArray(data) ? data : [];
    },

    async createHousehold(name) {
      await this.init();
      if (!this.isSignedIn() || !this.client) throw new Error('Sign in first');
      const { data, error } = await this.client.rpc('create_household', {
        p_name: name || 'Family'
      });
      if (error) throw error;
      return data;
    },

    async createHouseholdInvite(householdId, label) {
      await this.init();
      if (!this.isSignedIn() || !this.client) throw new Error('Sign in first');
      if (!householdId) throw new Error('No household — create one first');
      const { data, error } = await this.client.rpc('create_household_invite', {
        p_household_id: householdId,
        p_label: label || null
      });
      if (error) {
        const msg = error.message || String(error);
        if (/function|does not exist|schema cache/i.test(msg)) {
          throw new Error('Invite SQL not on server — run schema-c1-household.sql in Supabase');
        }
        if (/gen_random_bytes|digest/i.test(msg)) {
          throw new Error('Invite crypto missing — run FIX-invite-gen-random-bytes.sql');
        }
        throw error;
      }
      // Supabase may return object or array
      if (Array.isArray(data)) return data[0] || data;
      return data;
    },

    async acceptHouseholdInvite(token) {
      await this.init();
      if (!this.isSignedIn() || !this.client) throw new Error('Sign in first');
      const { data, error } = await this.client.rpc('accept_household_invite', {
        p_token: String(token || '').trim()
      });
      if (error) throw error;
      return data;
    },

    async leaveHousehold(householdId) {
      await this.init();
      if (!this.isSignedIn() || !this.client) throw new Error('Sign in first');
      const { data, error } = await this.client.rpc('leave_household', {
        p_household_id: householdId
      });
      if (error) throw error;
      return data;
    },

    async getHouseholdLifeShare(householdId) {
      await this.init();
      if (!this.isSignedIn() || !this.client) throw new Error('Sign in first');
      const { data, error } = await this.client.rpc('get_household_life_share', {
        p_household_id: householdId
      });
      if (error) throw error;
      return data;
    },

    async upsertHouseholdLifeShare(householdId, payload, baseUpdatedAt) {
      await this.init();
      if (!this.isSignedIn() || !this.client) throw new Error('Sign in first');
      const { data, error } = await this.client.rpc('upsert_household_life_share', {
        p_household_id: householdId,
        p_payload: payload,
        p_base_updated_at: baseUpdatedAt || null
      });
      if (error) throw error;
      return data;
    },

    async getCalendarConnections() {
      await this.init();
      if (!this.isSignedIn() || !this.client) return [];
      try {
        const { data, error } = await this.client.rpc('my_calendar_connection_status');
        if (error) {
          log('calendar status', error.message);
          return [];
        }
        if (Array.isArray(data)) return data;
        if (data && typeof data === 'object') return Object.values(data);
        return [];
      } catch (err) {
        log('calendar status fail', err && err.message);
        return [];
      }
    },

    async startCalendarOAuth(provider) {
      await this.init();
      if (!this.isSignedIn()) throw new Error('Sign in to Harbor first');
      if (!this.client) throw new Error('Cloud not configured');
      const p = String(provider || 'google').toLowerCase();
      if (p === 'microsoft' || p === 'outlook' || p === 'azure') {
        throw new Error('Outlook calendar connect is not available. Use Google, phone calendars, or .ics import.');
      }
      if (p !== 'google') throw new Error('Only Google Calendar connect is supported');
      const { data: sessionData } = await this.client.auth.getSession();
      const token = sessionData && sessionData.session && sessionData.session.access_token;
      if (!token) throw new Error('Session expired — sign in again');
      const base = normalizeUrl(global.HARBOR_SUPABASE.url);
      const url = base + '/functions/v1/calendar-oauth-start';
      let res;
      try {
        const ctrl = typeof AbortController !== 'undefined' ? new AbortController() : null;
        const t = ctrl ? setTimeout(() => ctrl.abort(), 20000) : null;
        res = await fetch(url, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: 'Bearer ' + token,
            apikey: String(global.HARBOR_SUPABASE.anonKey || '')
          },
          body: JSON.stringify({
            provider: 'google',
            redirect_to: (global.location && global.location.origin
              ? global.location.origin + (global.location.pathname || '/')
              : '') || undefined
          }),
          signal: ctrl ? ctrl.signal : undefined
        });
        if (t) clearTimeout(t);
      } catch (err) {
        if (err && err.name === 'AbortError') {
          throw new Error('Calendar OAuth timed out — check Edge Functions are deployed');
        }
        throw new Error('Could not reach ' + url + ' — deploy calendar-oauth-start or check network');
      }
      let body = null;
      try { body = await res.json(); } catch (_) { body = null; }
      if (!res.ok) {
        const msg = (body && (body.error || body.message)) || ('OAuth start failed (' + res.status + ')');
        if (res.status === 404) {
          throw new Error('calendar-oauth-start not found (404) — deploy Edge Functions');
        }
        throw new Error(msg);
      }
      if (!body || !body.url) throw new Error('OAuth start did not return a URL — deploy calendar-oauth-start');
      return body;
    },

    async disconnectCalendarOAuth(provider) {
      await this.init();
      if (!this.isSignedIn()) throw new Error('Sign in to Harbor first');
      if (!this.client) throw new Error('Cloud not configured');
      const p = String(provider || 'google').toLowerCase();
      if (p === 'microsoft' || p === 'outlook' || p === 'azure') {
        throw new Error('Outlook calendar connect is not available.');
      }
      const { data: sessionData } = await this.client.auth.getSession();
      const token = sessionData && sessionData.session && sessionData.session.access_token;
      if (!token) throw new Error('Session expired — sign in again');
      const base = normalizeUrl(global.HARBOR_SUPABASE.url);
      const res = await fetch(base + '/functions/v1/calendar-oauth-disconnect', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: 'Bearer ' + token,
          apikey: String(global.HARBOR_SUPABASE.anonKey || '')
        },
        body: JSON.stringify({ provider: 'google' })
      });
      let body = null;
      try { body = await res.json(); } catch (_) { body = null; }
      if (!res.ok) {
        const msg = (body && (body.error || body.message)) || ('Disconnect failed (' + res.status + ')');
        throw new Error(msg);
      }
      return body || { ok: true };
    }
  };

  global.HarborCloud = Cloud;
})(typeof window !== 'undefined' ? window : globalThis);
