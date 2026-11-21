🇬🇧 **English** | 🇵🇱 [Wersja polska](README.pl.md)

# Characterization regression harness (legacy vs. new)

Upgrading the Python 3 / Django 1.11 application to Python 3.12 + Django 6.1
replaces the whole framework under it, so the safest proof of "same business
behaviour" is a **golden-master (characterization) comparison**: run the old and
the new application side by side, do exactly the same things in both and compare
what comes out.

## How it works

1. `run.sh` exports the baseline code from git (`LEGACY_REF`, default `b13f205` =
   the last pre-upgrade `master`) and builds it on its original stack
   (`legacy/Dockerfile`: Python 3.7 + Django 1.11).
2. The baseline (`legacy` service) and the current tree (`candidate`) start from
   **identical copies** of the seed database (`db.sqlite3` at `LEGACY_REF`, or
   `SEED_DB=path`). The candidate also runs `schema_check.py` (models vs. the real,
   partly hand-altered legacy schema).
3. `run_scenarios.py` replays the same journeys over HTTP against both:
   * anonymous visitor - all pages, course chapters, static files,
   * student - course pages, content opinions, code runner, hints, achievements, logout,
   * administrator - admin lists and forms, adding/changing objects (admin CRUD),
   * **security probes** - source code under `/static/`, CSRF, sandbox escape,
     tampered tests, infinite loop, malformed input (they show a vulnerability on
     the legacy side and its fix on the candidate side).
4. Responses are normalized (CSRF tokens, Bootstrap CDN tags, HTML escaping style,
   traceback carets, Django's own error pages and admin translations) and the
   business tables of both databases are dumped after the journeys.
5. `compare.py` diffs both recordings. Intentional changes are listed, each with
   its reason, in an allowlist; any other difference fails the run.

```bash
make regression                 # or: regression/run.sh
cat .regression/report.txt      # full diff report
```

Last result (legacy vs. React UI branch): 178 items, 140 identical, 38 expected,
0 unexpected.

## Allowlist (`expected_differences.json`)

| Key | Meaning |
|---|---|
| `"<actor>: <step> [<path>]"` | this step may differ; the value is the reason |
| `"db:<table>"` | this business table may differ after the journeys |
| `"_line_replacements"` | `from` → `to` line sequences applied to the legacy recording first (a reviewed markup change on many pages, e.g. the logout control) |
| `"_compare_page_markup": false` | HTML pages are compared by status/redirect only; AJAX responses, files, admin data and the database are still compared fully (used since the React UI rewrite - page markup is checked in a real browser by [`../e2e/`](../e2e/README.md)) |

Entries that did not occur are reported as *stale*, so the list stays honest.

## Options

| Variable | Default | Meaning |
|---|---|---|
| `LEGACY_REF` | `b13f205` | git revision used as the baseline |
| `SEED_DB` | `db.sqlite3` at `LEGACY_REF` | database both apps start from |
| `BASELINE_MODE` | `legacy` | `modern`: the baseline is a revision of the upgraded app, built with its own `Dockerfile` (`baseline-modern.override.yml`) |
| `EXPECTED_FILE` | `expected_differences.json` | allowlist file inside `regression/` |

Server contract of the React UI vs. the jQuery UI branch:

```bash
make regression-ui
# = BASELINE_MODE=modern LEGACY_REF=f88c010 \
#   EXPECTED_FILE=expected_differences.react-ui.json regression/run.sh
```

Last result: 178 items, 173 identical, 5 expected (removed legacy JS files), 0 unexpected.

## Files

| File | Purpose |
|---|---|
| `run.sh` | prepares `.regression/` (sources, database copies) and runs the compose file |
| `../docker-compose.regression.yml` | `legacy`, `candidate` and `runner` services |
| `legacy/Dockerfile` | Python 3.7 + Django 1.11 image of the legacy app |
| `start-legacy.sh`, `start-candidate.sh` | start-up of the two apps |
| `prepare_db.py` | sets known passwords for the journeys (Django 1.11 compatible) |
| `schema_check.py` | models vs. the legacy database schema |
| `run_scenarios.py` | the journeys, normalization, database dump |
| `compare.py` | the diff and the allowlist rules |
| `runner/Dockerfile` | Python 3.12 + requests + BeautifulSoup for the runner |

## Self-check

When the harness was created it was run legacy vs. legacy: 165/165 items identical
(the security probes were added later). This shows the journeys are deterministic,
so a difference always means a real change in behaviour.
