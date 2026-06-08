# PR: feat/start-dashboard
#
# Use a dashboard as the start page for EVERY authenticated user (not just
# Admin), instead of /superset/welcome/.
#
# A before_request hook redirects logged-in users from the welcome/index routes
# to the target dashboard. Correctness against the acceptance checks:
#   * No broken 302 / no loop -- only welcome/index paths are intercepted; the
#     dashboard route itself is never redirected.
#   * Anonymous users are skipped -> the login flow is untouched (no premature
#     302 to the dashboard before authentication).
#   * Role-independent -> works for Gamma and other non-Admin roles.
#
# Operational note: the dashboard must be Published and the user's role must
# have access to it and its datasets, else they are 403'd after the redirect
# (an access grant, not a redirect bug). See README.

import os

__all__ = ["FLASK_APP_MUTATOR"]

DEFAULT_DASHBOARD_ID = os.environ.get("SUPERSET_DEFAULT_DASHBOARD_ID", "1")

# Paths that should send a logged-in user to the default dashboard.
_WELCOME_PATHS = {
    "/",
    "/superset/welcome",
    "/superset/welcome/",
    "/welcome",
    "/welcome/",
}


def FLASK_APP_MUTATOR(app):  # noqa: N802
    from flask import redirect, request
    from flask_login import current_user

    target = f"/superset/dashboard/{DEFAULT_DASHBOARD_ID}/"

    @app.before_request
    def _redirect_to_default_dashboard():
        if request.path not in _WELCOME_PATHS:
            return None
        if not getattr(current_user, "is_authenticated", False):
            return None
        return redirect(target)
