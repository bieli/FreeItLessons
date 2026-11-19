# Characterization regression harness (legacy vs. new)

Upgrading Python 2.7/3.x-era Django 1.11 to Python 3.12 + Django 6.1 replaces
the whole framework under the application, so the safest proof of "same business
behaviour" is a **golden-master (characterization) comparison**:

1. `run.sh` exports the legacy code from git (`LEGACY_REF`, default `b13f205`)
   and builds it on its original stack (`legacy/Dockerfile`: Python 3.7 + Django 1.11).
2. The legacy app and the current tree (`candidate`) start from **identical copies**
   of the seed database (`db.sqlite3` at `LEGACY_REF`, or `SEED_DB=path`).
   The candidate also runs `schema_check.py` (models vs. the real legacy schema).
3. `run_scenarios.py` replays the same journeys over HTTP against both:
   anonymous visitor, student (course pages, content opinions, code runner,
   hints, achievements, logout) and administrator (admin CRUD).
4. Responses are normalized (CSRF tokens, bootstrap CDN tags, escaping style,
   traceback carets, Django's own error pages/translations) and the business
   tables of both databases are dumped after the journeys.
5. `compare.py` diffs both recordings. Intentional changes are listed, with a
   reason, in `expected_differences.json`; anything else fails the run.

```bash
make regression                 # or: regression/run.sh
cat .regression/report.txt      # full diff report
```

Self-check of the harness (legacy vs. legacy must give 0 differences) was done
when the harness was created: 165/165 identical.
