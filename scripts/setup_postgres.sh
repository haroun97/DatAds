#!/usr/bin/env bash
# Start PostgreSQL in Docker and run migrations + ingestion.
set -euo pipefail
cd "$(dirname "$0")/.."

export DATABASE_URL="postgresql+psycopg://datads:datads@localhost:5433/datads"

if command -v docker-compose &>/dev/null; then
  COMPOSE="docker-compose"
elif docker compose version &>/dev/null 2>&1; then
  COMPOSE="docker compose"
else
  echo "Error: install Docker Compose (docker-compose or docker compose plugin)"
  exit 1
fi

$COMPOSE up -d
echo "Waiting for PostgreSQL..."
for i in {1..30}; do
  if python3 -c "import psycopg; psycopg.connect('dbname=datads user=datads password=datads host=localhost port=5433')" 2>/dev/null; then
    break
  fi
  sleep 1
done

source venv/bin/activate
pip install -q -r requirements.txt

# Write .env with Postgres URL
grep -v '^DATABASE_URL=' .env.example 2>/dev/null | head -5 > .env.tmp || true
echo "DATABASE_URL=$DATABASE_URL" > .env
cat .env.tmp >> .env 2>/dev/null || true
rm -f .env.tmp

alembic upgrade head
python scripts/ingest_facebook.py

echo ""
echo "PostgreSQL ready on localhost:5433"
echo "Run: uvicorn app.main:app --reload"
