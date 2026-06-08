# PR: feat/custom-favicon
#
# Replace the favicon. `FAVICONS` is a first-class Superset config flag, so no
# frontend rebuild is needed. The image file is copied into Superset's static
# assets by the Dockerfile (assets/custom-favicon.png ->
# /app/superset/static/assets/images/custom-favicon.png).

__all__ = ["FAVICONS"]

FAVICONS = [{"href": "/static/assets/images/custom-favicon.png"}]
