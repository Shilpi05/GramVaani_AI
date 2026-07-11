"""
scheme_finder.py
------------------
Government scheme discovery page for GramVaani AI.

FUTURE INTEGRATION NOTE:
    This page will eventually call a recommendation model in `ai/llm`
    that matches a citizen's profile (age, income, occupation, state)
    to relevant government schemes stored in `backend/database`.
    Today it only shows the intended layout, with no logic.
"""

import streamlit as st

from frontend.components.theme import page_header, placeholder_card
from frontend.config.constants import (
    SCHEME_FINDER_CARD_TEXT,
    SCHEME_FINDER_CARD_TITLE,
    SCHEME_FINDER_EYEBROW,
    SCHEME_FINDER_PLACEHOLDER,
    SCHEME_FINDER_SUBTITLE,
    SCHEME_FINDER_TITLE,
)


def render() -> None:
    """Renders the Scheme Finder page."""
    page_header(
        title=SCHEME_FINDER_TITLE,
        subtitle=SCHEME_FINDER_SUBTITLE,
        eyebrow=SCHEME_FINDER_EYEBROW,
    )

    st.markdown(
        f"""
        <div class="gv-card">
            <h3>{SCHEME_FINDER_CARD_TITLE}</h3>
            <p>{SCHEME_FINDER_CARD_TEXT}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")
    st.divider()
    placeholder_card(icon="🎯", text=SCHEME_FINDER_PLACEHOLDER)
