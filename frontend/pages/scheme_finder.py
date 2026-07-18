"""
scheme_finder.py
------------------
Government scheme discovery page for GramVaani AI.

This page does NOT compute scheme matches itself. Matching happens
in `frontend/pages/file_complaint.py`, right after a complaint is
generated, because that's where the complaint data (type, department,
summary) the match is based on already exists - see
`ai/schemes/scheme_recommender.py` for the actual matching logic.

This page's only job is to READ the result of that match from
`st.session_state` (via `file_complaint.SCHEMES_STATE_KEY`) and
display it - the same separation of "compute where the data lives,
display where the user expects it" already used for complaint
tracking (`ai/utils/complaint_tracker.py` computes/stores, both Home
and Track Complaint independently read from it).

Two states:
    - No complaint filed yet this session -> empty state with a
      "File a Complaint" button.
    - Schemes available -> rendered exactly as they were previously
      shown directly on the File Complaint page (relocated here
      verbatim, not rewritten).
"""

import html

import streamlit as st

from frontend.components.theme import department_badge_html, page_header
from frontend.config.constants import (
    SCHEME_DEPARTMENT_LABEL,
    SCHEME_ELIGIBILITY_LABEL,
    SCHEME_FINDER_CARD_TEXT,
    SCHEME_FINDER_CARD_TITLE,
    SCHEME_FINDER_EMPTY_STATE_BUTTON_LABEL,
    SCHEME_FINDER_EMPTY_STATE_TEXT,
    SCHEME_FINDER_EYEBROW,
    SCHEME_FINDER_SUBTITLE,
    SCHEME_FINDER_TITLE,
    SCHEME_RECOMMENDATION_CARD_TITLE,
)
from frontend.pages.file_complaint import SCHEMES_STATE_KEY
from frontend.utils.helpers import navigate_to


def _render_schemes(schemes) -> None:
    """
    Renders the recommended government schemes, each as its own card
    - matching the same card language used everywhere else in the
    app (`.gv-card`, real `<h3>` titles, department badges), instead
    of the dash-separated plain-text block this used before. This was
    the last surface in the app still using that older format.

    If no matching schemes were found, a single explanatory line is
    shown instead of the scheme list.

    Args:
        schemes: Either a list of scheme dicts or the "no match"
            fallback string, exactly as stored by
            `file_complaint._handle_generate_complaint()`.
    """
    if isinstance(schemes, str):
        # No matching category - schemes holds the fallback message.
        st.markdown(
            f"""
            <div class="gv-card">
                <h3>{SCHEME_RECOMMENDATION_CARD_TITLE}</h3>
                <p>{html.escape(schemes)}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    st.markdown(
        f"<h3 class='gv-section-title'>{SCHEME_RECOMMENDATION_CARD_TITLE}</h3>",
        unsafe_allow_html=True,
    )

    for scheme in schemes:
        name = html.escape(str(scheme.get("name", "")))
        description = html.escape(str(scheme.get("description", "")))
        eligibility = html.escape(str(scheme.get("eligibility", "")))
        department_badge = department_badge_html(
            scheme.get("official_department", "")
        )

        st.markdown(
            f"""
            <div class="gv-card gv-scheme-card">
                <h3>🏛 {name}</h3>
                <p>{description}</p>
                <p><strong>{SCHEME_ELIGIBILITY_LABEL}:</strong> {eligibility}</p>
                <p><strong>{SCHEME_DEPARTMENT_LABEL}:</strong> {department_badge}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.write("")


def _render_empty_state() -> None:
    """
    Renders the empty state shown when no complaint has been filed
    yet this session, with a one-click button back to File Complaint.
    """
    st.markdown(
        f"""
        <div class="gv-placeholder-card">
            <div class="gv-placeholder-icon">🎯</div>
            <p>{SCHEME_FINDER_EMPTY_STATE_TEXT}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")
    _, center_col, _ = st.columns([1, 1, 1])
    with center_col:
        if st.button(
            SCHEME_FINDER_EMPTY_STATE_BUTTON_LABEL,
            use_container_width=True,
            type="primary",
            key="gv_scheme_finder_file_complaint_cta",
        ):
            navigate_to("file_complaint")


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

    schemes = st.session_state.get(SCHEMES_STATE_KEY)
    if not schemes:
        _render_empty_state()
    else:
        _render_schemes(schemes)
        