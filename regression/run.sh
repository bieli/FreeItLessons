#!/bin/sh
# Characterization regression check: legacy (Django 1.11) vs candidate (this tree).
#   LEGACY_REF  git revision with the legacy code      (default: b13f205 = last pre-upgrade master)
#   SEED_DB     database both apps start from          (default: db.sqlite3 at LEGACY_REF)
set -eu
cd "$(dirname "$0")/.."
LEGACY_REF=${LEGACY_REF:-b13f205}
WORK=.regression

rm -rf "$WORK"
mkdir -p "$WORK/legacy-src" "$WORK/legacy" "$WORK/candidate"
git archive "$LEGACY_REF" | tar -x -C "$WORK/legacy-src"
cp regression/legacy/Dockerfile "$WORK/legacy-src/Dockerfile.legacy"
if [ -n "${SEED_DB:-}" ]; then cp "$SEED_DB" "$WORK/seed.sqlite3"
else git show "$LEGACY_REF:db.sqlite3" > "$WORK/seed.sqlite3"; fi
cp "$WORK/seed.sqlite3" "$WORK/legacy/db.sqlite3"
cp "$WORK/seed.sqlite3" "$WORK/candidate/db.sqlite3"
chmod -R a+rwX "$WORK/legacy" "$WORK/candidate"

COMPOSE="docker compose -f docker-compose.regression.yml ${COMPOSE_OVERRIDE:+-f $COMPOSE_OVERRIDE}"
status=0
$COMPOSE up --build --abort-on-container-exit --exit-code-from runner || status=$?
$COMPOSE down -v --remove-orphans >/dev/null 2>&1 || true
exit $status
