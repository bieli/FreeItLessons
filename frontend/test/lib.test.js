import { describe, expect, it } from 'vitest';
import { encodeUtf8Base64 } from '../src/lib/utf8Base64';
import { assertColors } from '../src/lib/asserts';
import { formatDuration } from '../src/lib/useStopwatch';
import { ajax, HttpError } from '../src/lib/api';
import { readProps } from '../src/lib/islands';
import { staticUrl } from '../src/lib/context';
import { mockFetch, setContext } from './utils';

describe('encodeUtf8Base64', () => {
  it('encodes the UTF-8 bytes of the program', () => {
    expect(encodeUtf8Base64('abc')).toBe('YWJj');
    expect(encodeUtf8Base64('zażółć')).toBe('emHFvMOzxYLEhw==');
    expect(new TextDecoder().decode(Uint8Array.from(atob(encodeUtf8Base64('# żółw 🐢')), (c) => c.charCodeAt(0))))
      .toBe('# żółw 🐢');
  });
});

describe('assertColors', () => {
  const asserts = ["assert 'a' == f('a')", "assert 'b' == f('b')", "assert 'c' == f('c')"];
  it('all green when the tests passed', () => {
    expect(assertColors('ASSERTS TESTS - OK.', asserts)).toEqual(['green', 'green', 'green']);
  });
  it('failing assert and the following ones are red', () => {
    const output = "Traceback\n  File \"program.py\", line 3\n    assert 'b' == f('b')\nAssertionError";
    expect(assertColors(output, asserts)).toEqual(['green', 'darkred', 'darkred']);
  });
  it('keeps the legacy rule: no assert in the output -> nothing marked red', () => {
    expect(assertColors('NameError: x', asserts)).toEqual(['green', 'green', 'green']);
  });
});

it('formatDuration', () => {
  expect(formatDuration(0)).toBe('00:00:00');
  expect(formatDuration(3725)).toBe('01:02:05');
});

describe('ajax', () => {
  it('POSTs form data with CSRF token and XHR header', async () => {
    setContext({});
    const calls = mockFetch({ 'POST /x/': [200, 'OK'] });
    await expect(ajax('/x/', { method: 'POST', data: { a: 1 } })).resolves.toBe('OK');
    expect(calls[0].body.get('a')).toBe('1');
    expect(calls[0].body.get('csrfmiddlewaretoken')).toBe('TOKEN');
    expect(calls[0].headers['X-Requested-With']).toBe('XMLHttpRequest');
    expect(calls[0].headers['Content-Type']).toBe('application/x-www-form-urlencoded; charset=UTF-8');
  });
  it('GETs with a query string and raises HttpError on 4xx', async () => {
    const calls = mockFetch({ 'GET /y/': [400, 'content NOT EXISTS'] });
    const error = await ajax('/y/', { data: { id: 5 } }).catch((e) => e);
    expect(calls[0].url).toBe('/y/?id=5');
    expect(error).toBeInstanceOf(HttpError);
    expect(error.body).toBe('content NOT EXISTS');
  });
});

it('readProps merges data attributes, json_script and <template> html', () => {
  document.body.innerHTML = `
    <script type="application/json" id="p">{"faqs": [1, 2]}</script>
    <div data-island="X" data-props-id="p" data-content-id="7"><template><b>hi</b></template></div>`;
  expect(readProps(document.querySelector('[data-island]'))).toEqual({ faqs: [1, 2], contentId: '7', html: '<b>hi</b>' });
});

describe('staticUrl', () => {
  it('uses the STATIC_URL of the server', () => {
    setContext({ staticUrl: '/static/' });
    expect(staticUrl('mainapp/img/new.png')).toBe('/static/mainapp/img/new.png');
    setContext({ staticUrl: '/assets/v2/' });
    expect(staticUrl('a.png')).toBe('/assets/v2/a.png');
    setContext({ staticUrl: 'https://cdn.example.com/static/' });
    expect(staticUrl('a.png')).toBe('https://cdn.example.com/static/a.png');
  });

  it('falls back to /static/ for anything that is not a plain path or https address', () => {
    for (const bad of ['javascript:alert(1)//', '"><img src=x onerror=alert(1)>/', '/static/")', 'http://x/',
      '//evil.example/', '/static', '']) {
      setContext({ staticUrl: bad });
      expect(staticUrl('a.png'), bad).toBe('/static/a.png');
    }
  });
});
