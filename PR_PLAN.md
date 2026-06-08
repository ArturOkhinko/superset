# PR plan — Superset 6.1.0 customization

The assignment asks for **one Pull Request per change**, based on the `6.1.0`
tag and merged into `main`.

The config is split into per-task modules so **every branch adds only its own
files** — no shared-file edits, no merge conflicts, and each PR is independently
mergeable into `main`.

> Run `./make-prs.sh` to generate all 7 branches automatically (see README),
> then `git push --all` and open the PRs.

## Branch / file map

| # | Branch | What it does | Files added |
|---|--------|--------------|-------------|
| 1 | `feat/clickhouse-connect` | Install the ClickHouse driver | `docker/requirements-local.txt` |
| 2 | `feat/custom-favicon` | Replace the favicon | `assets/custom-favicon.png`, `docker/pythonpath/config_favicon.py` |
| 3 | `feat/custom-logo` | Replace the logo | `assets/custom-logo.png`, `docker/pythonpath/config_logo.py` |
| 4 | `feat/remove-watermark` | Remove "Powered by Apache Superset" | `docker/pythonpath/config_watermark.py`, `patches/0002-remove-watermark-frontend.patch` |
| 5 | `feat/start-dashboard` | Dashboard as start page for all users | `docker/pythonpath/config_start_dashboard.py` |
| 6 | `feat/strip-superset-prefix` | Drop `/superset/` from URLs | `docker/nginx/nginx.conf`, `docker/pythonpath/config_proxy.py` |
| 7 | `docs/readme` | Documentation | `README.md`, `PR_PLAN.md` |

Scaffolding shared by every branch lives on `main`: `Dockerfile`,
`docker-compose.yml`, `.env.example`, `docker/docker-init.sh`,
`docker/pythonpath/superset_config.py` (core + module loader), `.gitignore`.
The core loader imports each `config_*.py` under `try/except`, so a branch that
only contains some modules still loads cleanly.

---

## 1. `feat/clickhouse-connect`

`docker/requirements-local.txt` lists `clickhouse-connect`; the Dockerfile
`pip install`s it. Verify:

```bash
docker compose run --rm superset python -c "import clickhouse_connect; print(clickhouse_connect.__version__)"
```

## 2 & 3. `feat/custom-favicon` / `feat/custom-logo`

`FAVICONS` and `APP_ICON` are first-class config flags — no frontend rebuild.
The Dockerfile copies the PNGs from `assets/` into
`/app/superset/static/assets/images/`.

## 4. `feat/remove-watermark`

`superset/views/base.py` (6.1.0) computes:

```python
"show_watermark": ("superset-logo-horiz" not in appbuilder.app_icon),
```

So overriding `APP_ICON` (PR #3) *turns the attribution on*. `config_watermark.py`
forces it off via `COMMON_BOOTSTRAP_OVERRIDES_FUNC` (runtime, no rebuild). The
source-level alternative — deleting the line from
`superset-frontend/src/features/home/RightMenu.tsx` — is in
`patches/0002-remove-watermark-frontend.patch` (needs a frontend rebuild).

## 5. `feat/start-dashboard`

`config_start_dashboard.py` adds a `FLASK_APP_MUTATOR` `before_request` hook
that redirects logged-in users from `/`, `/welcome`, `/superset/welcome/` to
`/superset/dashboard/<DEFAULT_DASHBOARD_ID>/`.

* **No broken 302 / no loop** — only welcome/index paths are intercepted.
* **Anonymous users skipped** — `current_user.is_authenticated` guard keeps the
  login flow intact.
* **Works for non-Admin** — role-independent. The dashboard must be Published
  and the role (e.g. Gamma) granted access to it and its datasets, else 403.

## 6. `feat/strip-superset-prefix`

`docker/nginx/nginx.conf` 301s `/superset/<x>` → `/<x>`, rewrites clean app
routes back to `/superset/<x>` upstream, and strips `/superset/` from every
`Location` header (so login + start-dashboard 302 stay clean).
`config_proxy.py` sets `ENABLE_PROXY_FIX=True` so Superset honours the proxy
headers.

Pure source-level alternative (a larger PR): set `route_base = "/"` on the
`Superset` view in `superset/views/core.py`. It removes the prefix at the source
but touches every `url_for("Superset.*")` and risks route collisions, so the
proxy approach is preferred for production.
