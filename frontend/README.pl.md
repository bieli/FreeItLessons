🇬🇧 [English version](README.md) | 🇵🇱 **Polski**

# FreeItLessons - interfejs w React

Interaktywne części strony to małe komponenty **React 19** („wyspy”) budowane
przez **Vite**. Każdą stronę, adresy URL i treści nadal generuje Django; React
przejmuje tylko elementy, które mają coś robić (menu, okna dialogowe, edytor
kodu ...). jQuery nie jest już używane.

> Chcesz tylko uruchomić stronę? Nie potrzebujesz niczego z tego folderu - zrób to,
> co opisuje [Uruchom projekt na swoim komputerze](../README.pl.md#uruchom-projekt-na-swoim-komputerze-krok-po-kroku);
> Docker sam zbuduje interfejs w React.

## Jak działa wyspa

1. Szablon Django zawiera pusty element z nazwą komponentu i opcjonalnie jego dane:

   ```django
   <div data-island="FaqAccordion" data-props-id="faq-props"></div>
   {{ faqs_props|json_script:"faq-props" }}
   ```

2. Każda strona ładuje `/static/mainapp/dist/app.js`. Skrypt znajduje wszystkie
   elementy `[data-island]` i wyświetla w każdym z nich zarejestrowany komponent
   ([`src/lib/islands.jsx`](src/lib/islands.jsx)). Komponent dostaje jako propsy:
   * JSON wskazany przez `data-props-id` (element `json_script`),
   * pozostałe atrybuty `data-*` (`data-content-id="5"` → `contentId="5"`),
   * `html` - wnętrze elementu `<template>` umieszczonego w środku (używane dla
     treści kursów napisanych przez mentorów).
3. Dane potrzebne wszędzie pochodzą z JSON-a `frontend-context` na stronie
   (`mainapp/context_processors.py`) i odczytuje się je przez `getContext()`:
   `isAuthenticated`, `userId`, `username`, `csrfToken`, `staticUrl`.

| Wyspa | Strona | Zastępuje (dawny JS) |
|---|---|---|
| `NavBar` | każda strona (nagłówek) | Bootstrap 3 JS (menu na telefonie, rozwijane menu) + jQuery |
| `FaqAccordion` | FAQ | rozwijane odpowiedzi w jQuery |
| `RotatingStatusIcons`, `FloatingBackground` | strona główna | `animate` z jQuery, floating.js |
| `ContentBlock` + `OpinionDialog` | rozdział kursu | okno dialogowe jQuery UI, AJAX w jQuery |
| `TaskWorkspace` (osobny plik, ładowany tylko na stronach zadań) | zadanie | edit_area, highlight.js, jquery.base64, easytimer, AJAX w jQuery |
| `StatusPieChart` (wejście `admin.jsx`) | panel: statusy treści | skrypt z jQuery + Google Charts |

## Struktura folderu

```
frontend/
├── src/
│   ├── main.jsx               # rejestr wysp + ich montowanie (app.js)
│   ├── admin.jsx              # panel Django: wykres statusów (admin.js)
│   ├── lib/
│   │   ├── islands.jsx        # znajduje [data-island] i wyświetla komponenty
│   │   ├── context.js         # getContext(), staticUrl(), readJsonScript()
│   │   ├── api.js             # ajax(): fetch z X-Requested-With + tokenem CSRF
│   │   ├── utf8Base64.js      # program -> base64 z jego bajtów UTF-8
│   │   ├── asserts.js         # kolory listy asercji po uruchomieniu
│   │   └── useStopwatch.js    # czas spędzony nad zadaniem
│   ├── components/
│   │   ├── layout/            # NavBar, Collapse (animacja rozwijania)
│   │   ├── faq/               # FaqAccordion
│   │   ├── home/              # RotatingStatusIcons, FloatingBackground
│   │   ├── courses/           # ContentBlock, OpinionDialog
│   │   ├── task/              # TaskWorkspace, CodeEditor (CodeMirror 6), HighlightedCode
│   │   └── admin/             # StatusPieChart
│   └── styles/                # app.css, admin.css
├── test/                      # testy Vitest + Testing Library
├── vite.config.js
└── package.json
```

Zbudowane pliki trafiają do `../mainapp/static/mainapp/dist/` (nie są zapisywane
w gicie): `app.js`, `app.css`, `admin.js`, `admin.css` oraz pliki z hashem
w nazwie w `chunks/`.

## Polecenia

Potrzebujesz **Node.js 22+** - albo wcale go nie potrzebujesz, jeśli używasz Dockera.

| Polecenie (w `frontend/`) | Co robi |
|---|---|
| `npm ci` | instaluje dokładnie te wersje zależności, które są w `package-lock.json` |
| `npm run build` | build produkcyjny do `mainapp/static/mainapp/dist/` |
| `npm run dev` | przebudowuje po każdej zmianie (tryb deweloperski) - odśwież stronę, żeby zobaczyć efekt |
| `npm test` | uruchamia testy jednostkowe raz |
| `npm run test:watch` | uruchamia testy ponownie po każdej zmianie |

Bez Node, z folderu projektu: `docker compose run --rm frontend-tests`
(instaluje, testuje, buduje). `Dockerfile` buduje interfejs we własnym etapie
z Node, więc `docker compose up --build` zawsze serwuje świeżą wersję.

Typowa praca nad kodem (dwa terminale, w folderze projektu):

```bash
make run            # Django na http://127.0.0.1:8000 (najpierw buduje interfejs)
make frontend-dev   # przebudowuje interfejs po każdej zmianie
```

## Dodawanie nowej wyspy

1. Utwórz komponent, np. `src/components/hello/HelloBox.jsx`:

   ```jsx
   import { getContext } from '../../lib/context';

   export default function HelloBox({ greeting }) {
     const { username } = getContext();
     return <p className="text-info">{greeting}, {username || 'gościu'}!</p>;
   }
   ```

2. Zarejestruj go w [`src/main.jsx`](src/main.jsx): `registry = { ..., HelloBox }`.
3. Wstaw go do szablonu: `<div data-island="HelloBox" data-greeting="Cześć"></div>`.
4. Dodaj test w `test/` i uruchom `npm test`, a potem `npm run build`.

## Zasady, które warto znać

* **Wywołania Django:** używaj `ajax(url, { method, data })` z `lib/api.js` - wysyła
  dane formularza, nagłówek `X-Requested-With: XMLHttpRequest` (widoki go wymagają)
  i token CSRF przy żądaniach POST. Zmiany danych zawsze idą przez POST.
* **HTML od mentorów** (treści kursów, odpowiedzi w FAQ, podpowiedzi) to zaufana
  treść pisana w panelu administracyjnym i jest wstawiana przez
  `dangerouslySetInnerHTML`; nigdy nie rób tego z tekstem wpisanym przez uczniów.
* **Programy** są wysyłane jako base64 z ich bajtów UTF-8 (polskie litery są w porządku);
  testy zawsze pochodzą z bazy danych serwera.
* **Testy w przeglądarce:** ten sam zestaw testów Playwright ([`../e2e/`](../e2e/README.pl.md))
  działa na dawnym interfejsie jQuery i na tym interfejsie React (`make e2e`).
  Zachowaj identyfikatory elementów, z których korzystają (`program_run`,
  `program_output`, `asserts_list`, `hint-1` ... `hint-5`, `timerHtml`,
  `content_id__<id>`, nazwę pól wyboru `dialog-send-status-select`).
