# PR: feat/strip-superset-prefix
#
# Backend half of removing the /superset/ prefix. The nginx reverse proxy
# (docker/nginx/nginx.conf) does the URL translation; this flag makes Superset
# trust the X-Forwarded-* headers so cookies, redirects and absolute URLs are
# generated correctly behind the proxy.

__all__ = ["ENABLE_PROXY_FIX"]

ENABLE_PROXY_FIX = True
