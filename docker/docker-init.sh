#!/usr/bin/env bash
# =============================================================================
# One-shot initialization: run by the `init` service before the web server.
#   * applies database migrations
#   * creates the admin user
#   * syncs roles/permissions
#   * (optionally) loads the example dashboards/datasets
#   * creates a non-Admin (Gamma) demo user to verify the start-dashboard flow
# =============================================================================
set -euo pipefail

echo "==> Upgrading metadata database"
superset db upgrade

echo "==> Creating admin user"
superset fab create-admin \
  --username "${SUPERSET_ADMIN_USERNAME:-admin}" \
  --firstname "${SUPERSET_ADMIN_FIRST:-Superset}" \
  --lastname "${SUPERSET_ADMIN_LAST:-Admin}" \
  --email "${SUPERSET_ADMIN_EMAIL:-admin@example.com}" \
  --password "${SUPERSET_ADMIN_PASSWORD:-admin}" || true

echo "==> Initializing roles and permissions"
superset init

if [ "${SUPERSET_LOAD_EXAMPLES:-yes}" = "yes" ]; then
  echo "==> Loading example data (provides dashboard id 1)"
  superset load_examples || true
fi

echo "==> Creating a Gamma (non-admin) demo user to test the start dashboard"
superset fab create-user \
  --role Gamma \
  --username gamma \
  --firstname Gamma \
  --lastname User \
  --email gamma@example.com \
  --password gamma || true

echo "==> Init complete"
