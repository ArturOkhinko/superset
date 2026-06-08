# PR: feat/custom-logo
#
# Replace the Superset logo.
#
# Why APP_ICON alone is not enough in 6.x: the navbar logo is rendered from the
# THEME brand token `brandLogoUrl`. Upstream config.py freezes
# `"brandLogoUrl": APP_ICON` as a dict literal at config-load time using the
# DEFAULT icon, so overriding APP_ICON afterwards does not change the theme.
# We therefore rebuild THEME_DEFAULT / THEME_DARK from the upstream 6.1.0
# defaults, changing ONLY the brand fields -- every colour, font and the dark
# `algorithm` are preserved so the dark theme keeps working.
#
# The image file is copied into Superset's static assets by the Dockerfile
# (assets/custom-logo.png -> /app/superset/static/assets/images/custom-logo.png).
#
# NOTE: a custom logo makes the backend turn the "Powered by Apache Superset"
# attribution ON (see superset/views/base.py); that is removed by the
# feat/remove-watermark PR.

import os

__all__ = [
    "APP_NAME",
    "APP_ICON",
    "APP_ICON_WIDTH",
    "LOGO_TOOLTIP",
    "LOGO_TARGET_PATH",
    "THEME_DEFAULT",
    "THEME_DARK",
    "ENABLE_UI_THEME_ADMINISTRATION",
]

APP_NAME = os.environ.get("SUPERSET_APP_NAME", "DataHub Analytics")
APP_ICON = "/static/assets/images/custom-logo.png"
APP_ICON_WIDTH = 148
LOGO_TOOLTIP = APP_NAME
# Clicking the logo lands on the default dashboard rather than /welcome/
LOGO_TARGET_PATH = (
    f"/superset/dashboard/{os.environ.get('SUPERSET_DEFAULT_DASHBOARD_ID', '1')}/"
)

# Make config themes authoritative for branding. With the default (True), an
# admin-defined system theme stored in the DB can shadow these tokens and bring
# back the old logo; False guarantees the brand below is what users see.
# Flip back to True if you prefer DB/UI-managed themes (brand may then be
# overridable from the Theme admin UI).
ENABLE_UI_THEME_ADMINISTRATION = False

# Upstream 6.1.0 default tokens, with ONLY the brand fields customized.
_DEFAULT_TOKEN = {
    # Brand (customized) -------------------------------------------------------
    "brandAppName": APP_NAME,
    "brandLogoAlt": APP_NAME,
    "brandLogoUrl": APP_ICON,
    "brandLogoMargin": "18px 0",
    "brandLogoHref": LOGO_TARGET_PATH,
    "brandLogoHeight": "24px",
    # Spinner ------------------------------------------------------------------
    "brandSpinnerUrl": None,
    "brandSpinnerSvg": None,
    # Default colors (unchanged from upstream) ---------------------------------
    "colorPrimary": "#2893B3",
    "colorLink": "#2893B3",
    "colorError": "#e04355",
    "colorWarning": "#fcc700",
    "colorSuccess": "#5ac189",
    "colorInfo": "#66bcfe",
    # Fonts --------------------------------------------------------------------
    "fontUrls": [],
    "fontFamily": "Inter, Helvetica, Arial, sans-serif",
    "fontFamilyCode": "'IBM Plex Mono', 'Courier New', monospace",
    # Extra tokens -------------------------------------------------------------
    "transitionTiming": 0.3,
    "brandIconMaxWidth": 37,
    "fontSizeXS": "8",
    "fontSizeXXL": "28",
    "fontWeightNormal": "400",
    "fontWeightLight": "300",
    "fontWeightStrong": "500",
    "fontWeightBold": "700",
    "colorEditorSelection": "#fff5cf",
}

THEME_DEFAULT = {
    "token": dict(_DEFAULT_TOKEN),
    "algorithm": "default",
}

# Dark theme: inherit all tokens, swap the editor-selection colour and add the
# dark algorithm -- identical to upstream, so dark mode keeps working.
THEME_DARK = {
    "token": {**_DEFAULT_TOKEN, "colorEditorSelection": "#5c4d1a"},
    "algorithm": "dark",
}
