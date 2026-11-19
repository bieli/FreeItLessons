#!/bin/sh
# Browser level characterization: the same Playwright spec runs against
#   jquery   - BASE_REF (default: upgrade/python312-django61, the jQuery UI)
#   react    - the current working tree (React UI)
# Both start from identical copies of the seed database (db.sqlite3 at BASE_REF).
set -eu
cd "$(dirname "$0")/.."
BASE_REF=${BASE_REF:-upgrade/python312-django61}
WORK=.e2e

rm -rf "$WORK"
mkdir -p "$WORK/baseline-src" "$WORK/baseline" "$WORK/candidate" "$WORK/report"
git archive "$BASE_REF" | tar -x -C "$WORK/baseline-src"
git show "$BASE_REF:db.sqlite3" > "$WORK/seed.sqlite3"
cp "$WORK/seed.sqlite3" "$WORK/baseline/db.sqlite3"
cp "$WORK/seed.sqlite3" "$WORK/candidate/db.sqlite3"
chmod -R a+rwX "$WORK"

E2E_STUDENT=$(python3 -c "import sqlite3,sys; print(sqlite3.connect(sys.argv[1]).execute('select username from auth_user where id=2').fetchone()[0])" "$WORK/seed.sqlite3")
E2E_ADMIN=$(python3 -c "import sqlite3,sys; print(sqlite3.connect(sys.argv[1]).execute('select username from auth_user where id=1').fetchone()[0])" "$WORK/seed.sqlite3")
HOST_UID=$(id -u)
export E2E_STUDENT E2E_ADMIN HOST_UID
export E2E_TARGETS=${E2E_TARGETS:-jquery=http://baseline:8000,react=http://candidate:8000}

COMPOSE="docker compose -f docker-compose.e2e.yml"
status=0
$COMPOSE up --build --abort-on-container-exit --exit-code-from e2e ${E2E_SERVICES:-} || status=$?
$COMPOSE down -v --remove-orphans >/dev/null 2>&1 || true
echo "HTML report: $WORK/report/index.html"
exit $status
