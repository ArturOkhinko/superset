# Apache Superset 6.1.0 — Customized Production Image

A customized, production-style build of Apache Superset **6.1.0** with:

- ✅ `clickhouse-connect` baked into the image
- ✅ custom favicon
- ✅ custom logo
- ✅ "Powered by Apache Superset" removed from **Settings → About**
- ✅ a dashboard as the start page for **all** users (not just Admin)
- ✅ `/superset/` prefix removed from URLs (`/superset/dashboard/1` → `/dashboard/1`)

Each item is a separate, reviewable change — see [`PR_PLAN.md`](./PR_PLAN.md)
for the one-PR-per-task breakdown.

```
.
├── Dockerfile                  # custom image on top of apache/superset:6.1.0
├── docker-compose.yml          # production-like stack (nginx + web + worker + beat + db + redis)
├── .env.example                # configuration template
├── assets/                     # custom-logo.png, custom-favicon.png (placeholders — swap in your art)
├── docker/
│   ├── pythonpath/
│   │   ├── superset_config.py        # core config + loads the modules below
│   │   ├── config_favicon.py         # FAVICONS
│   │   ├── config_logo.py            # APP_ICON / branding
│   │   ├── config_watermark.py       # removes "Powered by Apache Superset"
│   │   ├── config_start_dashboard.py # start-page redirect
│   │   └── config_proxy.py           # ENABLE_PROXY_FIX
│   ├── requirements-local.txt  # clickhouse-connect
│   ├── docker-init.sh          # db upgrade + admin + roles + examples + demo Gamma user
│   └── nginx/nginx.conf        # reverse proxy that strips /superset/
├── patches/                    # optional upstream-style source patches
├── PR_PLAN.md                  # branch/PR map for each task
└── README.md
```

## 1. Build the Docker image

```bash
git clone <your-repo-url> superset-custom && cd superset-custom
cp .env.example .env
# REQUIRED: generate a strong secret
echo "SUPERSET_SECRET_KEY=$(openssl rand -base64 42)" >> .env

# Build the custom image (tagged custom-superset:6.1.0)
docker compose build
# or directly:
docker build --build-arg SUPERSET_VERSION=6.1.0 -t custom-superset:6.1.0 .
```

The image is built **on top of `apache/superset:6.1.0`**, which is itself
produced from the `apache/superset` sources at the `6.1.0` tag. This keeps each
customization a small layer and avoids a multi-hour frontend rebuild, while
still being "a 6.1.0 production image built from the official sources."

<details>
<summary><strong>Building purely from source (optional)</strong></summary>

To apply the source-level patches (e.g. the frontend watermark removal in
`patches/`), clone the upstream repo at the tag and build its own Dockerfile:

```bash
git clone --branch 6.1.0 --depth 1 https://github.com/apache/superset.git
cd superset
git apply ../patches/0002-remove-watermark-frontend.patch
docker build -t custom-superset:6.1.0 --target lean .
```

This recompiles the frontend bundle, so `.tsx` patches take effect. It is much
slower than the layered build above.
</details>

## 2. Run Superset

```bash
docker compose up -d
# follow first-run initialization (migrations, admin, examples):
docker compose logs -f init
```

Once `init` exits and `superset` is healthy, open **http://localhost** (nginx
on port 80).

Default logins (from `.env`):

| User | Role | Purpose |
|------|------|---------|
| `admin` / `admin` | Admin | full access |
| `gamma` / `gamma` | Gamma | verify the start dashboard works for non-Admins |

### Verifying the acceptance criteria

```bash
# /superset/ prefix is stripped (301 to the clean URL):
curl -sI http://localhost/superset/dashboard/1/ | grep -i location   # -> /dashboard/1/

# A logged-in non-Admin lands on the dashboard, not /welcome:
#   log in as gamma in the browser and hit http://localhost/welcome
#   -> 302 to /dashboard/1/  (no redirect loop, no bounce to /login)
```

For the Gamma user to actually *open* dashboard 1, publish it and grant access:
**log in as admin → open the dashboard → Edit → Publish**, then **Settings →
List Roles → Gamma** (or the dashboard's own **Access** roles with
`DASHBOARD_RBAC`) so Gamma can read the dashboard and its datasets. Without this
the redirect is correct but the user is 403'd — that is an access-grant step,
not a redirect bug.

## 3. What I'd change for a real production deployment

- **Secrets management.** `SUPERSET_SECRET_KEY` and DB credentials belong in a
  secrets manager (Vault / AWS Secrets Manager / Docker secrets), not `.env`.
  Rotate the key with the documented re-encryption procedure.
- **TLS everywhere.** Terminate HTTPS at nginx (or an ALB), set
  `SESSION_COOKIE_SECURE=true`, add HSTS, and force HTTP→HTTPS.
- **Managed datastores.** Use a managed Postgres (backups, PITR, replicas) and
  managed Redis (or separate cache vs. broker instances) instead of containers
  with local volumes.
- **Scale the tiers independently.** Run web, Celery worker and beat as
  separate, horizontally-scaled deployments; size Gunicorn workers/threads to
  CPU. On Kubernetes use the Helm chart with HPA and a `PodDisruptionBudget`.
- **Real auth.** Wire SSO (OAuth/OIDC/LDAP) via `AUTH_TYPE`, map IdP groups to
  Superset roles with `AUTH_ROLES_MAPPING`, and disable open self-registration.
- **Observability.** Ship logs to a central store, expose `/health` to the
  orchestrator, add StatsD/Prometheus metrics, and configure Sentry.
- **CSP & hardening.** Enable `TALISMAN_ENABLED` with a tuned Content-Security-
  Policy, keep CSRF on, and put a WAF / rate limiting in front.
- **Async queries & results.** Enable `GLOBAL_ASYNC_QUERIES`, move SQL Lab and
  chart results to a dedicated results backend (e.g. S3), and set sensible row
  limits and query timeouts.
- **Pin & scan.** Pin the base image by digest, run image vulnerability scans
  in CI, and gate releases on `superset` health checks.
- **The `/superset/` prefix.** For a deployment that must *never* emit the
  prefix internally, ship the source-level `route_base = "/"` change (see
  `PR_PLAN.md`) instead of relying only on the nginx rewrite.

---

### Notes

- Superset **6.1.0** is a real upstream release (rc1 March 2026; final mid-2026).
- The placeholder logo/favicon in `assets/` are generated brand art ("DataHub")
  — replace them with your own files of the same names and rebuild.
