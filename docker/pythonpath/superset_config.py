# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements. See the NOTICE file.
#
# Core production configuration for Apache Superset 6.1.0.
#
# Loaded via SUPERSET_CONFIG_PATH=/app/pythonpath/superset_config.py.
# This file holds the version-neutral CORE settings (DB, Redis, Celery,
# hardening). Each customization task lives in its own `config_*.py` module in
# this same directory and is merged in at the bottom -- so every task is an
# independent, conflict-free file (one Pull Request each):
#
#   config_favicon.py         -> PR: feat/custom-favicon
#   config_logo.py            -> PR: feat/custom-logo
#   config_watermark.py       -> PR: feat/remove-watermark
#   config_start_dashboard.py -> PR: feat/start-dashboard
#   config_proxy.py           -> PR: feat/strip-superset-prefix
# -----------------------------------------------------------------------------

import os


def env(key: str, default=None):
    return os.environ.get(key, default)


# -----------------------------------------------------------------------------
# Core / secrets
# -----------------------------------------------------------------------------
SECRET_KEY = env("SUPERSET_SECRET_KEY", "CHANGE_ME_IN_PRODUCTION_use_openssl_rand")

SQLALCHEMY_DATABASE_URI = (
    f"postgresql+psycopg2://{env('DATABASE_USER', 'superset')}:"
    f"{env('DATABASE_PASSWORD', 'superset')}@"
    f"{env('DATABASE_HOST', 'db')}:{env('DATABASE_PORT', '5432')}/"
    f"{env('DATABASE_DB', 'superset')}"
)

# -----------------------------------------------------------------------------
# Caching & async (Redis)
# -----------------------------------------------------------------------------
REDIS_HOST = env("REDIS_HOST", "redis")
REDIS_PORT = env("REDIS_PORT", "6379")

CACHE_CONFIG = {
    "CACHE_TYPE": "RedisCache",
    "CACHE_DEFAULT_TIMEOUT": 300,
    "CACHE_KEY_PREFIX": "superset_",
    "CACHE_REDIS_HOST": REDIS_HOST,
    "CACHE_REDIS_PORT": REDIS_PORT,
    "CACHE_REDIS_DB": 1,
}
DATA_CACHE_CONFIG = {**CACHE_CONFIG, "CACHE_REDIS_DB": 2}
FILTER_STATE_CACHE_CONFIG = {**CACHE_CONFIG, "CACHE_REDIS_DB": 3}
EXPLORE_FORM_DATA_CACHE_CONFIG = {**CACHE_CONFIG, "CACHE_REDIS_DB": 4}


class CeleryConfig:
    broker_url = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"
    result_backend = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"
    imports = ("superset.sql_lab", "superset.tasks.scheduler")
    worker_prefetch_multiplier = 1
    task_acks_late = True


CELERY_CONFIG = CeleryConfig

# -----------------------------------------------------------------------------
# Production hardening
# -----------------------------------------------------------------------------
WTF_CSRF_ENABLED = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = env("SESSION_COOKIE_SECURE", "false").lower() == "true"
SESSION_COOKIE_SAMESITE = "Lax"

FEATURE_FLAGS = {
    "ALERT_REPORTS": True,
    "DASHBOARD_RBAC": True,
    "EMBEDDED_SUPERSET": True,
}

SQLLAB_CTAS_NO_LIMIT = True

# =============================================================================
# Merge in per-task customization modules (each is a separate PR / file).
# Missing modules are skipped, so any single branch loads cleanly on its own.
# =============================================================================
try:
    from config_favicon import *  # noqa: F401,F403
except ModuleNotFoundError:
    pass

try:
    from config_logo import *  # noqa: F401,F403
except ModuleNotFoundError:
    pass

try:
    from config_watermark import *  # noqa: F401,F403
except ModuleNotFoundError:
    pass

try:
    from config_start_dashboard import *  # noqa: F401,F403
except ModuleNotFoundError:
    pass

try:
    from config_proxy import *  # noqa: F401,F403
except ModuleNotFoundError:
    pass
