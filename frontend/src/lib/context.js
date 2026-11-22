// Server provided context ({{ frontend_context|json_script:"frontend-context" }}).
const DEFAULTS = { isAuthenticated: false, userId: null, username: '', csrfToken: '', staticUrl: '/static/' };

export function readJsonScript(id) {
  const el = document.getElementById(id);
  return el ? JSON.parse(el.textContent) : null;
}

export function getContext() {
  return { ...DEFAULTS, ...(readJsonScript('frontend-context') || {}) };
}

// STATIC_URL of Django: a path ("/static/") or an https address of a CDN, ending with "/".
// Anything else (quotes, "<", "javascript:" ...) is ignored, the value ends up in
// src attributes and CSS url("...").
const SAFE_STATIC_URL = /^(\/|https:\/\/[A-Za-z0-9.-]+(:\d+)?\/)([A-Za-z0-9_.~-]+\/)*$/;

export function staticUrl(path) {
  const base = getContext().staticUrl;
  return (SAFE_STATIC_URL.test(base) ? base : DEFAULTS.staticUrl) + path;
}
