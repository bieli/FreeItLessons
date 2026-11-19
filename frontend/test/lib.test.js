import { describe, expect, it } from 'vitest';
import { encodeLatin1Base64, UnsupportedCharacterError } from '../src/lib/latin1Base64';
import { assertColors } from '../src/lib/asserts';
import { formatDuration } from '../src/lib/useStopwatch';
import { ajax, HttpError } from '../src/lib/api';
import { readProps } from '../src/lib/islands';
import { mockFetch, setContext } from './utils';

describe('encodeLatin1Base64 (wire compatible with jquery.base64)', () => {
  it('encodes like the legacy plugin', () => {
    expect(encodeLatin1Base64('abc')).toBe('YWJj');
    expect(encodeLatin1Base64('SWÓJ KOD')).toBe('U1fTSiBLT0Q='); // value produced by jquery.base64
  });
  it('rejects characters the server cannot decode', () => {
    expect(() => encodeLatin1Base64('zażółć')).toThrow(UnsupportedCharacterError);
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
