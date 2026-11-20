🇬🇧 **English** | 🇵🇱 [Wersja polska](README.pl.md)

# FreeItLessons - React UI

The interactive parts of the website are small **React 19** components
("islands") built with **Vite**. Django still renders every page, the URLs and the
contents; React only takes over the elements that need behaviour (menus, dialogs,
the code editor ...). There is no jQuery any more.

> Just want to run the website? You don't need anything from this folder - follow
> [Run it on your computer](../README.md#run-it-on-your-computer-step-by-step);
> Docker builds the React UI for you.

## How an island works

1. A Django template contains an empty element with the component's name and,
   optionally, its data:

   ```django
   <div data-island="FaqAccordion" data-props-id="faq-props"></div>
   {{ faqs_props|json_script:"faq-props" }}
   ```

2. Every page loads `/static/mainapp/dist/app.js`. It finds all `[data-island]`
   elements and renders the registered component into each of them
   ([`src/lib/islands.jsx`](src/lib/islands.jsx)). The component gets as props:
   * the JSON from `data-props-id` (a `json_script` element),
   * the other `data-*` attributes (`data-content-id="5"` → `contentId="5"`),
   * `html` - the inner HTML of a `<template>` inside the element (used for
     course contents written by mentors).
3. Data needed everywhere comes from the page's `frontend-context` JSON
   (`mainapp/context_processors.py`), read with `getContext()`:
   `isAuthenticated`, `userId`, `username`, `csrfToken`, `staticUrl`.

| Island | Page | Replaces (former JS) |
|---|---|---|
| `NavBar` | every page (header) | Bootstrap 3 JS (mobile menu, dropdown) + jQuery |
| `FaqAccordion` | FAQ | jQuery slide accordion |
| `RotatingStatusIcons`, `FloatingBackground` | home | jQuery `animate`, floating.js |
| `ContentBlock` + `OpinionDialog` | course chapter | jQuery UI dialog, jQuery AJAX |
| `TaskWorkspace` (separate chunk, loaded only on task pages) | task | edit_area, highlight.js, jquery.base64, easytimer, jQuery AJAX |
| `StatusPieChart` (entry `admin.jsx`) | admin: content statuses | jQuery + Google Charts script |

## Folder structure

```
frontend/
├── src/
│   ├── main.jsx               # registry of islands + mounting (app.js)
│   ├── admin.jsx              # Django admin: status chart (admin.js)
│   ├── lib/
│   │   ├── islands.jsx        # finds [data-island] and renders components
│   │   ├── context.js         # getContext(), staticUrl(), readJsonScript()
│   │   ├── api.js             # ajax(): fetch with X-Requested-With + CSRF token
│   │   ├── utf8Base64.js      # program -> base64 of its UTF-8 bytes
│   │   ├── asserts.js         # colours of the assert list after a run
│   │   └── useStopwatch.js    # time spent on a task
│   ├── components/
│   │   ├── layout/            # NavBar, Collapse (slide animation)
│   │   ├── faq/               # FaqAccordion
│   │   ├── home/              # RotatingStatusIcons, FloatingBackground
│   │   ├── courses/           # ContentBlock, OpinionDialog
│   │   ├── task/              # TaskWorkspace, CodeEditor (CodeMirror 6), HighlightedCode
│   │   └── admin/             # StatusPieChart
│   └── styles/                # app.css, admin.css
├── test/                      # Vitest + Testing Library tests
├── vite.config.js
└── package.json
```

The build output goes to `../mainapp/static/mainapp/dist/` (not stored in git):
`app.js`, `app.css`, `admin.js`, `admin.css` and hashed files in `chunks/`.

## Commands

You need **Node.js 22+** - or no Node at all if you use Docker.

| Command (in `frontend/`) | What it does |
|---|---|
| `npm ci` | installs the exact dependency versions from `package-lock.json` |
| `npm run build` | production build into `mainapp/static/mainapp/dist/` |
| `npm run dev` | rebuilds on every change (development mode) - refresh the page to see it |
| `npm test` | runs the unit tests once |
| `npm run test:watch` | runs the tests again on every change |

Without Node, from the project folder: `docker compose run --rm frontend-tests`
(installs, tests, builds). The `Dockerfile` builds the UI in its own Node stage,
so `docker compose up --build` always serves a fresh bundle.

Typical development loop (two terminals, from the project folder):

```bash
make run            # Django on http://127.0.0.1:8000 (builds the bundle first)
make frontend-dev   # rebuild the bundle on every change
```

## Adding a new island

1. Create the component, e.g. `src/components/hello/HelloBox.jsx`:

   ```jsx
   import { getContext } from '../../lib/context';

   export default function HelloBox({ greeting }) {
     const { username } = getContext();
     return <p className="text-info">{greeting}, {username || 'guest'}!</p>;
   }
   ```

2. Register it in [`src/main.jsx`](src/main.jsx): `registry = { ..., HelloBox }`.
3. Put it into a template: `<div data-island="HelloBox" data-greeting="Hello"></div>`.
4. Add a test in `test/` and run `npm test`, then `npm run build`.

## Rules worth knowing

* **Calling Django:** use `ajax(url, { method, data })` from `lib/api.js` - it sends
  form data, the `X-Requested-With: XMLHttpRequest` header (the views require it)
  and the CSRF token for POST requests. State changes are always POST.
* **HTML from mentors** (course contents, FAQ answers, hints) is trusted, admin
  written content and is inserted with `dangerouslySetInnerHTML`; never do that with
  text typed by students.
* **Programs** are sent as base64 of their UTF-8 bytes (Polish letters are fine);
  the tests always come from the server's database.
* **Browser tests:** the same Playwright spec ([`../e2e/`](../e2e/)) runs against the
  former jQuery UI and this React UI (`make e2e`). Keep the element ids they use
  (`program_run`, `program_output`, `asserts_list`, `hint-1` ... `hint-5`,
  `timerHtml`, `content_id__<id>`, the radio name `dialog-send-status-select`).
