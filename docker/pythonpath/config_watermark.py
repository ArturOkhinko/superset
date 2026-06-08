# PR: feat/remove-watermark
#
# Remove "Powered by Apache Superset" from Settings -> About.
#
# In 6.1.0 the watermark is a backend-controlled attribution, computed in
# superset/views/base.py as:
#
#     "show_watermark": ("superset-logo-horiz" not in appbuilder.app_icon)
#
# i.e. replacing the default logo (feat/custom-logo) turns it ON. We force it
# back OFF by mutating the bootstrap payload before it reaches the frontend.
# No frontend rebuild required.
#
# A source-level alternative (editing RightMenu.tsx) is provided in
# patches/0002-remove-watermark-frontend.patch.

__all__ = ["COMMON_BOOTSTRAP_OVERRIDES_FUNC"]


def COMMON_BOOTSTRAP_OVERRIDES_FUNC(data):  # noqa: N802
    try:
        data["menu_data"]["navbar_right"]["show_watermark"] = False
    except (KeyError, TypeError):
        pass
    return {}
