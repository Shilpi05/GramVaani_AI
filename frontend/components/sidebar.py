"""
sidebar.py
-----------
Renders the left navigation sidebar for GramVaani AI.

Responsibilities:
    - Display the app logo / name
    - Render clickable navigation items
    - Update st.session_state["current_page"] when an item is clicked

This module contains ONLY UI/navigation logic. No business logic,
no AI calls, no backend calls belong here.

Translatable text (nav labels, the app title's "GramVaani" prefix,
and the tagline) comes from `frontend/utils/i18n.py` via `t()`, so it
updates immediately when the citizen changes Application Language on
the Settings page - no other wiring needed, since Streamlit reruns
the whole script on every interaction. Everything else non-
translatable (icons, the sidebar footer's version string) still comes
from `frontend/config/constants.py`, exactly as before.
"""

import streamlit as st

from frontend.config.constants import (
    DEFAULT_PAGE,
    NAV_ITEMS,
    SIDEBAR_BRAND_ICON,
    SIDEBAR_FOOTER,
)
from frontend.utils.i18n import t


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
        # Brand header. "AI" is kept as a literal, untranslated span
        # (a fixed, globally recognized acronym, styled in teal by
        # frontend/components/theme.py) - only the "GramVaani" prefix
        # is looked up via t().
        st.markdown(
            f"""
            <div class="gv-sidebar-brand">
                <span class="gv-sidebar-brand-icon">{SIDEBAR_BRAND_ICON}</span>
                <span class="gv-sidebar-brand-text">{t("sidebar.app_title_prefix")} <span>AI</span></span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<p class='gv-sidebar-tagline'>{t('sidebar.tagline')}</p>",
            unsafe_allow_html=True,
        )
        st.divider()

        # Navigation buttons - text-only labels (no icon prefix).
        for item in NAV_ITEMS:
            is_active = st.session_state["current_page"] == item["key"]
            nav_label = t("nav." + item["key"])

            if st.button(
                nav_label,
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