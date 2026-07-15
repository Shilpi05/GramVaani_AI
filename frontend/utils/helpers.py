"""
helpers.py
-----------
Shared, stateless helper functions used across multiple pages.

Kept intentionally small: only promote a function here once it's
genuinely needed in more than one page, to avoid speculative
abstractions. `navigate_to()` was the first such case - originally
defined privately inside `frontend/pages/home.py`, then needed again
by `frontend/pages/scheme_finder.py`'s empty-state "File a Complaint"
button, so it now lives here instead of being duplicated per page.
"""

import streamlit as st


def navigate_to(page_key: str) -> None:
    """
    Switches the active page using the same `st.session_state`
    mechanism `frontend/components/sidebar.py` already uses - this is
    frontend page routing, not backend logic.

    Args:
        page_key: A key from `NAV_ITEMS` in `frontend/config/constants.py`
            (e.g. "file_complaint", "track_complaint").
    """
    st.session_state["current_page"] = page_key
    st.rerun()