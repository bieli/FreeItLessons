// Server provided context ({{ frontend_context|json_script:"frontend-context" }}).
const DEFAULTS = { isAuthenticated: false, userId: null, username: '', csrfToken: '', staticUrl: '/static/' };

export function readJsonScript(id) {
  const el = document.getElementById(id);
  return el ? JSON.parse(el.textContent) : null;
}

export function getContext() {
  return { ...DEFAULTS, ...(readJsonScript('frontend-context') || {}) };
}

export function staticUrl(path) {
  return getContext().staticUrl + path;
}
