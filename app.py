"""
app.py
-------
Entry point for the GramVaani AI Streamlit application.

This file is intentionally thin. Its only job is to:
    1. Configure the page (title, icon, layout)
    2. Load the global theme (CSS injection), honoring the citizen's
       saved theme preference from the Settings page
    3. Load the sidebar and get the active page
    4. Route to the correct page's `render()` function

All actual page content lives in `frontend/pages/`.
All shared UI pieces (sidebar, theme) live in `frontend/components/`.
All static text/navigation data lives in `frontend/config/constants.py`.
"""

from typing import Callable, Dict

import streamlit as st

from frontend.components.sidebar import render_sidebar
from frontend.components.theme import inject_global_styles
from frontend.config.constants import APP_ICON, APP_NAME, DEFAULT_DARK_MODE
from frontend.pages import (
    file_complaint,
    home,
    scheme_finder,
    settings,
    track_complaint,
)

# ----------------------------------------------------------------------
# Page registry: maps a sidebar key -> the module's render() function.
# To add a new page in future: add a page file + one line here
# (plus one entry in NAV_ITEMS inside frontend/config/constants.py).
# ----------------------------------------------------------------------
PAGE_ROUTER: Dict[str, Callable[[], None]] = {
    "home": home.render,
    "file_complaint": file_complaint.render,
    "scheme_finder": scheme_finder.render,
    "track_complaint": track_complaint.render,
    "settings": settings.render,
}


def configure_page() -> None:
    """Sets global Streamlit page configuration. Must run first."""
    st.set_page_config(
        page_title=APP_NAME,
        page_icon=APP_ICON,
        layout="wide",
        initial_sidebar_state="expanded",
    )


def main() -> None:
    """Application entry point."""
    configure_page()
    dark_mode = st.session_state.get("gv_dark_mode", DEFAULT_DARK_MODE)
    inject_global_styles(dark_mode=dark_mode)

    active_page_key = render_sidebar()

    # Route to the selected page's render function.
    # Falls back to Home if an unknown key ever appears.
    render_fn = PAGE_ROUTER.get(active_page_key, home.render)
    render_fn()


if __name__ == "__main__":
    main()
