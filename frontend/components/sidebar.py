"""
sidebar.py
-----------
Renders the left navigation sidebar for GramVaani AI.

Responsibilities:
    - Display the app logo / name
    - Render clickable navigation items
    - Update st.session_state["current_page"] when an item is clicked

This module contains ONLY UI/navigation logic. No business logic,
no AI calls, no backend calls belong here. All text content comes
from `frontend/config/constants.py` - nothing is hardcoded here.
"""

import streamlit as st

from frontend.config.constants import (
    DEFAULT_PAGE,
    NAV_ITEMS,
    SIDEBAR_BRAND_ICON,
    SIDEBAR_FOOTER,
    SIDEBAR_TAGLINE,
)


def _init_session_state() -> None:
    """Ensures the current page is tracked in session_state."""
    if "current_page" not in st.session_state:
        st.session_state["current_page"] = DEFAULT_PAGE


def render_sidebar() -> str:
    """
    Renders the sidebar navigation and returns the currently
    selected page key (e.g. "home", "file_complaint").

    Returns:
        The key of the page that should currently be rendered.
    """
    _init_session_state()

    with st.sidebar:
        # Brand header
        st.markdown(
            f"""
            <div class="gv-sidebar-brand">
                <span class="gv-sidebar-brand-icon">{SIDEBAR_BRAND_ICON}</span>
                <span class="gv-sidebar-brand-text">GramVaani <span>AI</span></span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<p class='gv-sidebar-tagline'>{SIDEBAR_TAGLINE}</p>",
            unsafe_allow_html=True,
        )
        st.divider()

        # Navigation buttons
        for item in NAV_ITEMS:
            is_active = st.session_state["current_page"] == item["key"]
            button_label = f"{item['icon']}  {item['label']}"

            if st.button(
                button_label,
                key=f"nav_{item['key']}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
            ):
                st.session_state["current_page"] = item["key"]
                st.rerun()

        st.divider()
        st.markdown(
            f"<p class='gv-sidebar-footer'>{SIDEBAR_FOOTER}</p>",
            unsafe_allow_html=True,
        )

    return st.session_state["current_page"]
