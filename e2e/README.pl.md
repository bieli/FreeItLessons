🇬🇧 [English version](README.md) | 🇵🇱 **Polski**

# Testy w przeglądarce (Playwright): interfejs jQuery vs React

Przy przepisywaniu interfejsu z jQuery na React trzeba było odpowiedzieć na
pytanie: *czy nowy interfejs robi dokładnie to samo co stary?* Odpowiedź
sprawdzamy w prawdziwej przeglądarce (Chromium): **ten sam zestaw testów działa
na obu interfejsach** i na obu musi przejść.

| Projekt | Co testuje | Źródło |
|---|---|---|
| `jquery` | dawny interfejs jQuery | gałąź `BASE_REF` (domyślnie `upgrade/python312-django61`) |
| `react` | interfejs React | bieżący kod w folderze projektu |

Obie aplikacje startują z identycznych kopii przykładowej bazy danych
(`db.sqlite3` z `BASE_REF`), więc testy widzą te same kursy, zadania i konta.

## Uruchomienie

Potrzebujesz tylko Dockera (oraz `git` i `python3`, których `run.sh` używa do
przygotowania danych):

```bash
make e2e            # albo: e2e/run.sh
```

Polecenie buduje trzy kontenery (`baseline`, `candidate` oraz `e2e` z Playwrightem),
uruchamia wszystkie testy, wypisuje wynik i usuwa kontenery. Raport HTML ze
zrzutami ekranu i nagraniami (*trace*) nieudanych testów jest w pliku
**`.e2e/report/index.html`** (otwórz go w przeglądarce).

Ostatni wynik: **34 zaliczone** - React 17/17, jQuery 13/17 + 4 znane błędy
(oczekiwane niepowodzenia, zobacz niżej).

## Opcje

| Zmienna | Domyślnie | Znaczenie |
|---|---|---|
| `BASE_REF` | `upgrade/python312-django61` | rewizja gita z interfejsem jQuery (wersja bazowa) |
| `E2E_TARGETS` | `jquery=http://baseline:8000,react=http://candidate:8000` | projekty Playwrighta w postaci `nazwa=adres,...` |

Resztę `run.sh` ustawia sam: nazwy kont ucznia i administratora (konta nr 2 i 1
z bazy danych) oraz znane hasło (`regression/prepare_db.py`).

## Co jest testowane

| Plik | Działanie |
|---|---|
| `navigation.spec.js` | menu publiczne i link do logowania; menu ucznia, rozwijane menu użytkownika, wylogowanie; menu na telefonie |
| `faq.spec.js` | odpowiedzi w FAQ rozwijają się pojedynczo |
| `home.spec.js` | ikonki statusów obracają się na swoje miejsce; tło z unoszącymi się elementami jest animowane |
| `courses.spec.js` | ocena lekcji: wymagane logowanie, wymagany wybór, ikonka zmienia się i zostaje zapisana; *Cancel* zostawia poprzednią ocenę |
| `task.spec.js` | kod startowy uruchamia się po otwarciu, licznik czasu, kolorowanie testów; podpowiedzi odblokowują się po kolei; polskie litery (UTF-8); poprawne rozwiązanie przechodzi wszystkie testy i dostaje ★ |
| `admin.spec.js` | wykres statusów treści w panelu administracyjnym |

### Znane błędy interfejsu jQuery

Błędy znalezione w starym interfejsie nie są ukrywane: test oznaczony
`knownJqueryBug(...)` (czyli `test.fail` z Playwrighta) w projekcie `jquery`
**musi się nie udać** (i zostanie zgłoszony, jeśli nagle przejdzie), a w projekcie
`react` musi przejść.

| Test | Dlaczego interfejs jQuery nie przechodzi |
|---|---|
| rozwijane menu użytkownika na stronie głównej | `home.html` ładuje jQuery + Bootstrap JS drugi raz - menu otwiera się i od razu zamyka |
| menu na telefonie na stronie głównej | ten sam podwójny Bootstrap JS - otwartego menu nie da się zamknąć |
| polskie litery w programie | `jquery.base64` zgłasza błąd przy znakach powyżej U+00FF - *uruchom* po cichu nic nie robi |
| wykres statusów treści | `content_status_stats.js` używa niezdefiniowanej zmiennej `$` - wykres nigdy się nie wyświetlał |

### Automatyczne sprawdzenia w każdym teście

* **Brak błędów JavaScript w React:** `tests/fixtures.js` oznacza test `react` jako
  nieudany, jeśli strona zgłosi nieobsłużony błąd (błędy interfejsu jQuery są tylko
  zapisywane w raporcie).
* **Edytor kodu to wymieniony komponent:** `setEditorCode()` z `tests/helpers.js`
  wpisuje kod do edit_area (jQuery) albo do CodeMirror (React) - cała reszta to ten
  sam kod dla obu interfejsów.

## Pisanie nowego testu

```js
const { test, expect } = require('./fixtures');   // nie '@playwright/test'
const { login } = require('./helpers');

test('uczeń widzi listę zadań', async ({ page }) => {
  await login(page);                     // loguje konto ucznia
  await page.goto('/zadania.html');
  await expect(page.getByRole('link', { name: 'reverse_chars' })).toBeVisible();
});
```

Wskazówki:

* Używaj selektorów, które istnieją w **obu** interfejsach: widocznych tekstów
  i ról (`getByRole`, `getByText`) albo celowo zachowanych identyfikatorów
  (`program_run`, `program_output`, `asserts_list`, `hint-1` ... `hint-5`,
  `timerHtml`, `content_id__<id>`, nazwa pól wyboru `dialog-send-status-select`).
* Czekaj tak, jak czekałby człowiek: używaj `expect(...)` (ponawia sprawdzanie)
  zamiast stałych pauz; tylko animacje mogą wymagać krótkiego `waitForTimeout`.
* Testy uruchamiają się jeden po drugim (`workers: 1`) i zmieniają dane (oceny,
  rozwiązania) - pisz każdy test tak, żeby nie zależał od innego.
* Znalazłeś błąd w interfejsie jQuery? Oznacz test przez
  `knownJqueryBug(test, testInfo, 'powód')`.

## Pliki

| Plik | Do czego służy |
|---|---|
| `run.sh` | przygotowuje `.e2e/` (kod wersji bazowej, kopie bazy, nazwy kont) i uruchamia plik compose |
| `../docker-compose.e2e.yml` | usługi `baseline`, `candidate` i `e2e` |
| `Dockerfile` | obraz Playwrighta z zależnościami testów |
| `start-app.sh` | uruchamia jedną aplikację (migracje, hasła testowe, gunicorn) |
| `playwright.config.js` | projekty z `E2E_TARGETS`, raport, uruchamianie po kolei |
| `tests/fixtures.js` | wspólny `test` ze sprawdzeniem „brak błędów JavaScript” |
| `tests/helpers.js` | `login`, `setEditorCode`, `collectAlerts`, `rotation`, `knownJqueryBug` |
| `tests/*.spec.js` | testy |

Zobacz też: [testy regresji po stronie serwera](../regression/README.pl.md)
(HTTP + baza danych) oraz [interfejs w React](../frontend/README.pl.md).
