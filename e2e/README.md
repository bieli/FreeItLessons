🇬🇧 **English** | 🇵🇱 [Wersja polska](README.pl.md)

# Browser tests (Playwright): jQuery UI vs. React UI

When the jQuery UI was rewritten in React, the question was: *does the new UI do
exactly what the old one did?* The answer is checked in a real browser
(Chromium): **one test spec runs against both UIs** and must pass on both.

| Project | What it tests | Source |
|---|---|---|
| `jquery` | the former jQuery UI | branch `BASE_REF` (default `upgrade/python312-django61`) |
| `react` | the React UI | the current working tree |

Both apps start from identical copies of the example database (`db.sqlite3` at
`BASE_REF`), so the tests see the same courses, tasks and accounts.

## Run it

You only need Docker (and `git` + `python3`, which `run.sh` uses to prepare the data):

```bash
make e2e            # or: e2e/run.sh
```

It builds three containers (`baseline`, `candidate`, `e2e` with Playwright),
runs all tests, prints the result and removes the containers. The HTML report
with screenshots and traces of failures is in **`.e2e/report/index.html`**
(open it in a browser).

Last result: **34 passed** - React 17/17, jQuery 13/17 + 4 known defects
(expected failures, see below).

## Options

| Variable | Default | Meaning |
|---|---|---|
| `BASE_REF` | `upgrade/python312-django61` | git revision with the jQuery UI (the baseline) |
| `E2E_TARGETS` | `jquery=http://baseline:8000,react=http://candidate:8000` | Playwright projects as `name=url,...` |

`run.sh` sets the rest automatically: the student and admin usernames (accounts 2
and 1 of the seed database) and a known password (`regression/prepare_db.py`).

## What is tested

| Spec | Behaviour |
|---|---|
| `navigation.spec.js` | public menu and login link; student menu, user dropdown, logout; mobile menu toggle |
| `faq.spec.js` | FAQ answers open one at a time |
| `home.spec.js` | status icons rotate into place; floating background is animated |
| `courses.spec.js` | rating a lesson: login required, choice required, icon updated and saved; *Cancel* keeps the old rating |
| `task.spec.js` | starter code runs on open, timer, highlighted tests; hints unlock one by one; Polish letters (UTF-8); a correct solution passes all tests and gets a ★ |
| `admin.spec.js` | the content status chart in the admin |

### Known defects of the jQuery UI

Bugs found in the old UI are not hidden: the test is marked with
`knownJqueryBug(...)` (Playwright's `test.fail`), so on the `jquery` project it
**must fail** (and is reported if it suddenly passes), while on `react` it must pass.

| Test | Why the jQuery UI fails |
|---|---|
| user dropdown on the home page | `home.html` loads jQuery + Bootstrap JS a second time - the dropdown opens and closes at once |
| mobile: menu toggle on the home page | the same double Bootstrap JS - the open menu cannot be closed |
| Polish letters in the program | `jquery.base64` throws on characters above U+00FF - *run* silently does nothing |
| content status chart | `content_status_stats.js` uses an undefined global `$` - the chart never rendered |

### Automatic checks in every test

* **No JavaScript errors on React:** `tests/fixtures.js` fails a `react` test if the
  page throws an uncaught error (errors of the jQuery UI are only noted in the report).
* **The code editor is the replaced component:** `setEditorCode()` in
  `tests/helpers.js` fills edit_area (jQuery UI) or CodeMirror (React) - everything
  else is the same code for both UIs.

## Writing a new test

```js
const { test, expect } = require('./fixtures');   // not '@playwright/test'
const { login } = require('./helpers');

test('student sees the tasks list', async ({ page }) => {
  await login(page);                     // logs in the student account
  await page.goto('/zadania.html');
  await expect(page.getByRole('link', { name: 'reverse_chars' })).toBeVisible();
});
```

Tips:

* Use selectors that exist in **both** UIs: visible texts and roles
  (`getByRole`, `getByText`) or the element ids kept on purpose (`program_run`,
  `program_output`, `asserts_list`, `hint-1` ... `hint-5`, `timerHtml`,
  `content_id__<id>`, radio name `dialog-send-status-select`).
* Wait like a person would: use `expect(...)` (it retries) instead of fixed sleeps;
  only animations may need a short `waitForTimeout`.
* Tests run one after another (`workers: 1`) and change data (ratings, solutions) -
  write each test so it doesn't depend on another one.
* Found a bug of the jQuery UI? Mark the test with `knownJqueryBug(test, testInfo, 'reason')`.

## Files

| File | Purpose |
|---|---|
| `run.sh` | prepares `.e2e/` (baseline sources, database copies, usernames) and runs the compose file |
| `../docker-compose.e2e.yml` | `baseline`, `candidate` and `e2e` services |
| `Dockerfile` | Playwright image with the test dependencies |
| `start-app.sh` | starts one application (migrations, test passwords, gunicorn) |
| `playwright.config.js` | projects from `E2E_TARGETS`, reporter, sequential run |
| `tests/fixtures.js` | shared `test` with the "no JavaScript errors" check |
| `tests/helpers.js` | `login`, `setEditorCode`, `collectAlerts`, `rotation`, `knownJqueryBug` |
| `tests/*.spec.js` | the tests |

See also: [server side regression harness](../regression/README.md) (HTTP + database)
and the [React UI](../frontend/README.md).
