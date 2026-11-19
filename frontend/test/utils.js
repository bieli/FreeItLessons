export function setContext(context) {
  document.head.querySelectorAll('#frontend-context').forEach((el) => el.remove());
  const script = document.createElement('script');
  script.type = 'application/json';
  script.id = 'frontend-context';
  script.textContent = JSON.stringify({ staticUrl: '/static/', csrfToken: 'TOKEN', ...context });
  document.head.appendChild(script);
}

export const STUDENT = { isAuthenticated: true, userId: 2, username: 'student' };

/** fetch mock answering by "METHOD url-path" keys; records the calls. */
export function mockFetch(routes) {
  const calls = [];
  const fetchMock = async (url, init = {}) => {
    const method = init.method || 'GET';
    const path = url.split('?')[0];
    calls.push({ method, url, path, body: init.body ? new URLSearchParams(init.body) : null, headers: init.headers });
    const route = routes[`${method} ${path}`];
    const [status, body] = typeof route === 'function' ? route(calls.at(-1)) : (route || [404, '']);
    return { ok: status < 400, status, statusText: status < 400 ? 'OK' : 'Bad Request', text: async () => body };
  };
  globalThis.fetch = fetchMock;
  return calls;
}
