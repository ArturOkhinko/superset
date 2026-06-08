# =============================================================================
# Custom production image for Apache Superset 6.1.0
# =============================================================================
# Base: the official 6.1.0 release image, itself built from the apache/superset
# sources at the `6.1.0` tag. Layering on it keeps each customization a small,
# reviewable change and avoids a multi-hour frontend rebuild. (A pure
# build-from-source path is documented in the README.)
#
# The build is written so that ANY single feature branch builds cleanly: it
# copies whole directories and guards the optional pip step, rather than naming
# files that may only exist on some branches.
# =============================================================================
ARG SUPERSET_VERSION=6.1.0
FROM apache/superset:${SUPERSET_VERSION}

USER root

# The apache/superset 6.x image runs from a uv-managed virtualenv at /app/.venv.
# A plain `pip install` lands in the SYSTEM python and is invisible at runtime,
# so every install below uses `uv pip install` against this venv.
ENV VIRTUAL_ENV=/app/.venv
ENV UV_PROJECT_ENVIRONMENT=/app/.venv

# ---------------------------------------------------------------------------
# Metadata-database driver. The lean apache/superset image does not bundle a
# Postgres driver, so install it in the core image. Required by
# SQLALCHEMY_DATABASE_URI (postgresql+psycopg2://...).
# ---------------------------------------------------------------------------
RUN uv pip install --no-cache psycopg2-binary

# ---------------------------------------------------------------------------
# Extra Python packages (PR: feat/clickhouse-connect adds clickhouse-connect to
# docker/requirements-local.txt). Guarded so the image builds even if absent.
# ---------------------------------------------------------------------------
COPY docker/ /app/custom-docker/
RUN if [ -f /app/custom-docker/requirements-local.txt ]; then \
        uv pip install --no-cache -r /app/custom-docker/requirements-local.txt; \
    fi

# ---------------------------------------------------------------------------
# Brand assets (PR: feat/custom-logo, feat/custom-favicon).
# APP_ICON / FAVICONS in the config point at these files.
# ---------------------------------------------------------------------------
COPY assets/ /app/superset/static/assets/images/

# ---------------------------------------------------------------------------
# Configuration: core superset_config.py + per-task config_*.py modules.
# ---------------------------------------------------------------------------
COPY docker/pythonpath/ /app/pythonpath/
ENV SUPERSET_CONFIG_PATH=/app/pythonpath/superset_config.py
ENV PYTHONPATH=/app/pythonpath

RUN chown -R superset:superset /app/superset/static/assets/images /app/pythonpath
USER superset
