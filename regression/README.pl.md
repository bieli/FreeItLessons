🇬🇧 [English version](README.md) | 🇵🇱 **Polski**

# Testy charakteryzacyjne (stara wersja vs nowa)

Aktualizacja aplikacji w Pythonie 3 / Django 1.11 do Pythona 3.12 + Django 6.1
wymienia cały framework pod spodem, dlatego najpewniejszym dowodem na „to samo
działanie biznesowe” jest **porównanie ze złotym wzorcem (testy
charakteryzacyjne)**: uruchamiamy starą i nową aplikację obok siebie, robimy
w obu dokładnie to samo i porównujemy wyniki.

## Jak to działa

1. `run.sh` eksportuje z gita kod bazowy (`LEGACY_REF`, domyślnie `b13f205` =
   ostatni `master` sprzed aktualizacji) i buduje go na oryginalnym stosie
   (`legacy/Dockerfile`: Python 3.7 + Django 1.11).
2. Wersja bazowa (usługa `legacy`) i bieżący kod (`candidate`) startują
   z **identycznych kopii** bazy danych (`db.sqlite3` z `LEGACY_REF` albo
   `SEED_DB=ścieżka`). Nowa wersja uruchamia dodatkowo `schema_check.py`
   (modele vs prawdziwy, częściowo ręcznie zmieniany schemat starej bazy).
3. `run_scenarios.py` odtwarza przez HTTP te same scenariusze w obu aplikacjach:
   * anonimowy gość - wszystkie strony, rozdziały kursów, pliki statyczne,
   * uczeń - strony kursów, oceny treści, uruchamianie kodu, podpowiedzi,
     osiągnięcia, wylogowanie,
   * administrator - listy i formularze panelu, dodawanie i zmiana obiektów,
   * **sondy bezpieczeństwa** - kod źródłowy pod `/static/`, CSRF, ucieczka
     z piaskownicy, podmienione testy, nieskończona pętla, niepoprawne dane
     (pokazują lukę w starej wersji i jej poprawkę w nowej).
4. Odpowiedzi są normalizowane (tokeny CSRF, tagi CDN Bootstrapa, sposób
   escapowania HTML, znaczniki `^^^` w tracebackach, własne strony błędów
   i tłumaczenia panelu Django), a po scenariuszach zapisywana jest zawartość
   tabel biznesowych obu baz danych.
5. `compare.py` porównuje oba nagrania. Zamierzone zmiany są wypisane, każda
   z powodem, na liście dozwolonych różnic; każda inna różnica oznacza błąd.

```bash
make regression                 # albo: regression/run.sh
cat .regression/report.txt      # pełny raport różnic
```

Ostatni wynik (stara wersja vs gałąź z interfejsem React): 178 elementów,
140 identycznych, 38 oczekiwanych, 0 nieoczekiwanych.

## Lista dozwolonych różnic (`expected_differences.json`)

| Klucz | Znaczenie |
|---|---|
| `"<aktor>: <krok> [<ścieżka>]"` | ten krok może się różnić; wartość to powód |
| `"db:<tabela>"` | ta tabela biznesowa może się różnić po scenariuszach |
| `"_line_replacements"` | sekwencje linii `from` → `to` zamieniane najpierw w nagraniu starej wersji (sprawdzona zmiana kodu HTML na wielu stronach, np. przycisk wylogowania) |
| `"_compare_page_markup": false` | strony HTML są porównywane tylko po statusie i przekierowaniu; odpowiedzi AJAX, pliki, dane panelu i baza danych nadal są porównywane w całości (od przepisania interfejsu na React - kod stron sprawdzają testy w prawdziwej przeglądarce w [`../e2e/`](../e2e/)) |

Wpisy, które się nie wydarzyły, są zgłaszane jako *nieaktualne* (*stale*),
więc lista nie zawiera martwych wyjątków.

## Opcje

| Zmienna | Domyślnie | Znaczenie |
|---|---|---|
| `LEGACY_REF` | `b13f205` | rewizja gita używana jako wersja bazowa |
| `SEED_DB` | `db.sqlite3` z `LEGACY_REF` | baza, od której startują obie aplikacje |
| `BASELINE_MODE` | `legacy` | `modern`: wersja bazowa to rewizja już zaktualizowanej aplikacji, budowana jej własnym `Dockerfile` (`baseline-modern.override.yml`) |
| `EXPECTED_FILE` | `expected_differences.json` | plik z listą dozwolonych różnic w katalogu `regression/` |

Kontrakt serwera interfejsu React vs gałąź z interfejsem jQuery:

```bash
make regression-ui
# = BASELINE_MODE=modern LEGACY_REF=upgrade/python312-django61 \
#   EXPECTED_FILE=expected_differences.react-ui.json regression/run.sh
```

Ostatni wynik: 178 elementów, 173 identyczne, 5 oczekiwanych (usunięte stare
pliki JS), 0 nieoczekiwanych.

## Pliki

| Plik | Do czego służy |
|---|---|
| `run.sh` | przygotowuje `.regression/` (kod źródłowy, kopie bazy) i uruchamia plik compose |
| `../docker-compose.regression.yml` | usługi `legacy`, `candidate` i `runner` |
| `legacy/Dockerfile` | obraz starej aplikacji: Python 3.7 + Django 1.11 |
| `start-legacy.sh`, `start-candidate.sh` | uruchamianie obu aplikacji |
| `prepare_db.py` | ustawia znane hasła na potrzeby scenariuszy (zgodny z Django 1.11) |
| `schema_check.py` | modele vs schemat starej bazy danych |
| `run_scenarios.py` | scenariusze, normalizacja, zrzut bazy danych |
| `compare.py` | porównanie i reguły listy dozwolonych różnic |
| `runner/Dockerfile` | Python 3.12 + requests + BeautifulSoup dla uruchamiacza scenariuszy |

## Samosprawdzenie

Po stworzeniu narzędzia uruchomiono je w trybie „stara wersja vs stara wersja”:
165/165 elementów identycznych (sondy bezpieczeństwa dodano później). To pokazuje,
że scenariusze są powtarzalne, więc każda różnica oznacza prawdziwą zmianę
działania.
