// Calls of the Django AJAX endpoints, wire compatible with the former jQuery.ajax():
// form encoded data, X-Requested-With header, CSRF token in the POST body.
import { getContext } from './context';

export class HttpError extends Error {
  constructor(response, body) {
    super(`HTTP ${response.status}`);
    this.status = response.status;
    this.statusText = response.statusText;
    this.body = body;
  }
}

export async function ajax(url, { method = 'GET', data = {} } = {}) {
  const params = new URLSearchParams();
  Object.entries(data).forEach(([key, value]) => params.append(key, value ?? ''));
  const headers = { 'X-Requested-With': 'XMLHttpRequest' };
  let target = url;
  const init = { method, headers, credentials: 'same-origin' };
  if (method === 'GET') {
    target = `${url}?${params}`;
  } else {
    if (!params.has('csrfmiddlewaretoken')) params.append('csrfmiddlewaretoken', getContext().csrfToken);
    headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8';
    init.body = params.toString();
  }
  const response = await fetch(target, init);
  const body = await response.text();
  if (!response.ok) throw new HttpError(response, body);
  return body;
}
