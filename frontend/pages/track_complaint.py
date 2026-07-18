"""
track_complaint.py
--------------------
Complaint tracking page for GramVaani AI.

This is a MOCK tracking system:
    - No database of any kind - complaints are only trackable if they
      were generated during the CURRENT browser session (stored in
      `st.session_state` via `ai/utils/complaint_tracker.py`).
    - No authentication - anyone who knows a Complaint ID generated
      in this session can look up its status.
    - Status is not set by any real workflow; it is derived
      automatically from elapsed time since generation, cycling
      through four fixed stages:

          Submitted -> Under Review -> Assigned -> Resolved

Flow:
    1. Citizen enters a Complaint ID (e.g. "GV-20260713-00001") -
       the same ID shown at the top of the generated complaint card
       on the "File Complaint" page.
    2. Citizen clicks "Track Complaint".
    3. If a complaint with that ID was registered this session, its
       Status, Department, Date, and Priority are displayed, along
       with a simple visual progress stepper.
    4. If not found (wrong ID, or generated in a different/earlier
       session), a clear explanatory message is shown instead.
"""

import html

import streamlit as st

from ai.utils.complaint_tracker import (
    SESSION_STATE_REGISTRY_KEY,
    STATUS_STAGES,
    get_tracking_info,
)
from frontend.components.theme import (
    COLOR_BORDER,
    COLOR_NAVY,
    COLOR_TEAL,
    COLOR_TEAL_SOFT,
    COLOR_TEXT_MUTED,
    COLOR_WHITE,
    department_badge_html,
    page_header,
    priority_badge_html,
)
from frontend.config.constants import (
    TRACK_COMPLAINT_BUTTON_LABEL,
    TRACK_COMPLAINT_CARD_TEXT,
    TRACK_COMPLAINT_CARD_TITLE,
    TRACK_COMPLAINT_DATE_LABEL,
    TRACK_COMPLAINT_DEPARTMENT_LABEL,
    TRACK_COMPLAINT_EMPTY_ID_WARNING,
    TRACK_COMPLAINT_EYEBROW,
    TRACK_COMPLAINT_ID_INPUT_LABEL,
    TRACK_COMPLAINT_ID_INPUT_PLACEHOLDER,
    TRACK_COMPLAINT_NOT_FOUND_WARNING,
    TRACK_COMPLAINT_PRIORITY_LABEL,
    TRACK_COMPLAINT_RESULT_CARD_TITLE,
    TRACK_COMPLAINT_STATUS_LABEL,
    TRACK_COMPLAINT_SUBTITLE,
    TRACK_COMPLAINT_TITLE,
)

# Session-state keys used to persist the last tracking query's result
# across reruns, so it stays visible after the button click completes
# (same pattern used on the File Complaint page).
_TRACK_RESULT_KEY: str = "gv_track_last_result"
_TRACK_MESSAGE_KEY: str = "gv_track_last_message"


def _get_registry() -> dict:
    """
    Returns the mock complaint tracking registry backing dict, stored
    in `st.session_state`, creating it if this is the first time this
    session has touched it.

    Returns:
        The registry dict (complaint_id -> tracked complaint record).
    """
    return st.session_state.setdefault(SESSION_STATE_REGISTRY_KEY, {})


def _build_status_stepper_html(current_status: str) -> str:
    """
    Builds the HTML (plus its own scoped <style> block) for a simple
    horizontal progress stepper across the four fixed status stages,
    highlighting completed, current, and upcoming stages differently.

    Returns a string rather than calling `st.markdown()` directly, so
    the caller can splice it into one larger, single `st.markdown()`
    call alongside the rest of the result card. This matters because
    every line here is built with NO leading whitespace: Streamlit's
    Markdown renderer treats 4+ leading spaces on a line as an
    indented code block, so mixing indented multi-line f-strings
    across several st.markdown() calls previously caused this exact
    HTML to render as literal code text instead of an actual stepper
    (and also, separately, split the enclosing <div class="gv-card">
    open/close tags across three independent st.markdown() calls,
    which are each rendered as isolated HTML fragments - an open tag
    can never span across calls). Both bugs are avoided by building
    one flat, unindented string here and rendering the whole card in
    a single st.markdown() call from `_render_tracking_result`.

    Args:
        current_status: One of `STATUS_STAGES`. If it isn't
            recognized (should not normally happen), every stage is
            shown as "upcoming".

    Returns:
        A single-line-per-tag HTML string with no leading whitespace.
    """
    try:
        current_index = STATUS_STAGES.index(current_status)
    except ValueError:
        current_index = -1

    step_parts = []
    for index, stage in enumerate(STATUS_STAGES):
        if index < current_index:
            state = "done"
            marker = "&#10003;"  # checkmark
        elif index == current_index:
            state = "current"
            marker = str(index + 1)
        else:
            state = "upcoming"
            marker = str(index + 1)

        step_parts.append(
            f'<div class="gv-step gv-step-{state}">'
            f'<div class="gv-step-marker">{marker}</div>'
            f'<div class="gv-step-label">{html.escape(stage)}</div>'
            f"</div>"
        )
        if index < len(STATUS_STAGES) - 1:
            connector_state = "done" if index < current_index else "upcoming"
            step_parts.append(
                f'<div class="gv-step-connector gv-step-connector-{connector_state}"></div>'
            )

    stepper_style = (
        "<style>"
        ".gv-stepper{display:flex;align-items:center;margin:1rem 0 0.5rem 0;}"
        ".gv-step{display:flex;flex-direction:column;align-items:center;min-width:84px;}"
        ".gv-step-marker{width:30px;height:30px;border-radius:999px;display:flex;"
        "align-items:center;justify-content:center;font-weight:700;font-size:0.85rem;"
        "margin-bottom:0.4rem;}"
        f".gv-step-done .gv-step-marker{{background-color:{COLOR_TEAL};color:{COLOR_WHITE};}}"
        f".gv-step-current .gv-step-marker{{background-color:{COLOR_TEAL};color:{COLOR_WHITE};"
        f"box-shadow:0 0 0 4px {COLOR_TEAL_SOFT};}}"
        f".gv-step-upcoming .gv-step-marker{{background-color:{COLOR_WHITE};color:{COLOR_TEXT_MUTED};"
        f"border:1.5px solid {COLOR_BORDER};}}"
        ".gv-step-label{font-size:0.78rem;text-align:center;font-weight:600;}"
        f".gv-step-done .gv-step-label,.gv-step-current .gv-step-label{{color:{COLOR_NAVY};}}"
        f".gv-step-upcoming .gv-step-label{{color:{COLOR_TEXT_MUTED};font-weight:500;}}"
        ".gv-step-connector{flex:1;height:3px;margin:0 0.25rem 1.6rem 0.25rem;border-radius:2px;}"
        f".gv-step-connector-done{{background-color:{COLOR_TEAL};}}"
        f".gv-step-connector-upcoming{{background-color:{COLOR_BORDER};}}"
        "</style>"
    )

    return stepper_style + '<div class="gv-stepper">' + "".join(step_parts) + "</div>"


def _render_tracking_result(result: dict) -> None:
    """
    Renders the tracking result card: Complaint ID header, the status
    stepper, and the Status / Department / Date / Priority fields -
    all as a single, flat HTML string in one `st.markdown()` call
    (see `_build_status_stepper_html` for why this matters).

    Args:
        result: The dict returned by
            `ai.utils.complaint_tracker.get_tracking_info()`.
    """
    complaint_id = html.escape(str(result.get("complaint_id", "")))
    status = str(result.get("status", ""))
    department_badge = department_badge_html(result.get("department", ""))
    tracked_date = html.escape(str(result.get("date", "")))
    priority_badge = priority_badge_html(result.get("priority", ""))

    stepper_html = _build_status_stepper_html(status)

    card_html = (
        '<div class="gv-card">'
        f"<h3>{TRACK_COMPLAINT_RESULT_CARD_TITLE}</h3>"
        f"<p><strong>Complaint ID:</strong> {complaint_id}</p>"
        f"{stepper_html}"
        f"<p><strong>{TRACK_COMPLAINT_STATUS_LABEL}:</strong> {html.escape(status)}</p>"
        f"<p><strong>{TRACK_COMPLAINT_DEPARTMENT_LABEL}:</strong> {department_badge}</p>"
        f"<p><strong>{TRACK_COMPLAINT_DATE_LABEL}:</strong> {tracked_date}</p>"
        f"<p><strong>{TRACK_COMPLAINT_PRIORITY_LABEL}:</strong> {priority_badge}</p>"
        "</div>"
    )

    st.write("")
    st.markdown(card_html, unsafe_allow_html=True)


def render() -> None:
    """Renders the Track Complaint page."""
    page_header(
        title=TRACK_COMPLAINT_TITLE,
        subtitle=TRACK_COMPLAINT_SUBTITLE,
        eyebrow=TRACK_COMPLAINT_EYEBROW,
    )

    st.markdown(
        f"""
        <div class="gv-card">
            <h3>{TRACK_COMPLAINT_CARD_TITLE}</h3>
            <p>{TRACK_COMPLAINT_CARD_TEXT}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")

    complaint_id_input = st.text_input(
        label=TRACK_COMPLAINT_ID_INPUT_LABEL,
        placeholder=TRACK_COMPLAINT_ID_INPUT_PLACEHOLDER,
        key="gv_track_complaint_id_input",
    )

    if st.button(
        TRACK_COMPLAINT_BUTTON_LABEL,
        use_container_width=True,
        type="primary",
        key="gv_track_complaint_button",
    ):
        query_id = (complaint_id_input or "").strip()

        if not query_id:
            st.session_state[_TRACK_RESULT_KEY] = None
            st.session_state[_TRACK_MESSAGE_KEY] = TRACK_COMPLAINT_EMPTY_ID_WARNING
        else:
            registry = _get_registry()
            info = get_tracking_info(registry, query_id)

            if info is None:
                st.session_state[_TRACK_RESULT_KEY] = None
                st.session_state[_TRACK_MESSAGE_KEY] = TRACK_COMPLAINT_NOT_FOUND_WARNING
            else:
                st.session_state[_TRACK_RESULT_KEY] = info
                st.session_state[_TRACK_MESSAGE_KEY] = None

    message = st.session_state.get(_TRACK_MESSAGE_KEY)
    if message:
        st.warning(message)

    result = st.session_state.get(_TRACK_RESULT_KEY)
    if result:
        _render_tracking_result(result)