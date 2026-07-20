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
       with a visual progress timeline.
    4. If not found (wrong ID, or generated in a different/earlier
       session), a professional empty-state card is shown instead.

Presentation note:
    The tracking *logic* (registration, lookup, status computation)
    lives entirely in `ai/utils/complaint_tracker.py` and is untouched
    by this file - the only backend change is that
    `get_tracking_info()` now also returns the "generated_at" ISO
    timestamp it already computed internally, so this page can derive
    display-only detail from it. Everything below is a presentation
    layer built on top of the same 4 STATUS_STAGES:
      - `DISPLAY_STAGES` / `_display_stage_progress()` re-expresses
        the backend's 4 stages as 5 more citizen-friendly timeline
        entries with real per-stage timestamps (splitting "Assigned"
        into "Assigned to Municipal Officer" and "Officer Visit
        Scheduled" for the timeline view only, using elapsed time
        within that stage to decide which of the two is current - the
        underlying status value driving all of this is still exactly
        one of the backend's 4 stages).
      - `_estimated_resolution_text()`, `_officer_remark_for_stage()`,
        and `_contact_for_department()` are static, priority/stage/
        department-keyed display strings (not backend fields) meant
        to read like a real grievance portal - a rough SLA, a
        plausible officer note, and a (clearly labeled mock) contact
        block.
"""

import html
from datetime import datetime, timedelta

import streamlit as st

from ai.utils.complaint_tracker import (
    SESSION_STATE_REGISTRY_KEY,
    STAGE_INTERVAL_SECONDS,
    STATUS_STAGES,
    get_tracking_info,
)
from frontend.components.theme import (
    department_badge_html,
    page_header,
    priority_badge_html,
    render_empty_state,
    resolved_banner_html,
    status_badge_html,
)
from frontend.config.constants import (
    TRACK_COMPLAINT_BUTTON_LABEL,
    TRACK_COMPLAINT_CARD_TEXT,
    TRACK_COMPLAINT_CARD_TITLE,
    TRACK_COMPLAINT_COMPLAINT_ID_LABEL,
    TRACK_COMPLAINT_CONTACT_CARD_TITLE,
    TRACK_COMPLAINT_CONTACT_DEPARTMENT_LABEL,
    TRACK_COMPLAINT_CONTACT_EMAIL_LABEL,
    TRACK_COMPLAINT_CONTACT_MOCK_NOTE,
    TRACK_COMPLAINT_CONTACT_OFFICER_LABEL,
    TRACK_COMPLAINT_CONTACT_PHONE_LABEL,
    TRACK_COMPLAINT_CURRENT_STAGE_TAG,
    TRACK_COMPLAINT_DATE_LABEL,
    TRACK_COMPLAINT_DEPARTMENT_LABEL,
    TRACK_COMPLAINT_EMPTY_ID_ICON,
    TRACK_COMPLAINT_EMPTY_ID_TITLE,
    TRACK_COMPLAINT_EMPTY_ID_WARNING,
    TRACK_COMPLAINT_ESTIMATED_RESOLUTION_LABEL,
    TRACK_COMPLAINT_EYEBROW,
    TRACK_COMPLAINT_ID_INPUT_LABEL,
    TRACK_COMPLAINT_ID_INPUT_PLACEHOLDER,
    TRACK_COMPLAINT_LAST_UPDATED_LABEL,
    TRACK_COMPLAINT_NOT_FOUND_ICON,
    TRACK_COMPLAINT_NOT_FOUND_TITLE,
    TRACK_COMPLAINT_NOT_FOUND_WARNING,
    TRACK_COMPLAINT_PRIORITY_LABEL,
    TRACK_COMPLAINT_REMARKS_CARD_TITLE,
    TRACK_COMPLAINT_RESULT_CARD_TITLE,
    TRACK_COMPLAINT_STATUS_LABEL,
    TRACK_COMPLAINT_SUBTITLE,
    TRACK_COMPLAINT_TIMELINE_CARD_TITLE,
    TRACK_COMPLAINT_TITLE,
)

# Session-state keys used to persist the last tracking query's result
# across reruns, so it stays visible after the button click completes
# (same pattern used on the File Complaint page).
_TRACK_RESULT_KEY: str = "gv_track_last_result"
_TRACK_MESSAGE_KEY: str = "gv_track_last_message"

# ----------------------------------------------------------------------
# Display-only timeline stages (see module docstring "Presentation
# note" above - this is a UI relabeling layered on the backend's 4
# STATUS_STAGES, not a change to the tracking pipeline itself).
# ----------------------------------------------------------------------
DISPLAY_STAGES = [
    "Complaint Submitted",
    "Under Review",
    "Assigned to Municipal Officer",
    "Officer Visit Scheduled",
    "Resolved",
]

# Display-only SLA copy, keyed by priority (case-insensitive). Purely
# informational for the citizen - not derived from, or fed back into,
# the backend tracking logic.
_ESTIMATED_RESOLUTION_BY_PRIORITY = {
    "high": "3\u20135 business days from submission",
    "medium": "7\u201310 business days from submission",
    "low": "14\u201315 business days from submission",
}
_ESTIMATED_RESOLUTION_FALLBACK = "To be confirmed by the assigned department"

# Display-only officer remarks, keyed by DISPLAY_STAGES label. Chosen
# to read like a plausible note from a municipal officer at each
# stage - not fetched from anywhere, since there is no real officer
# workflow behind this mock tracker.
_OFFICER_REMARKS = {
    "Complaint Submitted": (
        "Complaint received successfully and logged into the "
        "grievance system. It will be reviewed by the concerned "
        "department shortly."
    ),
    "Under Review": (
        "Complaint is being reviewed to verify the details and "
        "determine the appropriate department and priority."
    ),
    "Assigned to Municipal Officer": (
        "Complaint has been assigned to the concerned officer for "
        "necessary action."
    ),
    "Officer Visit Scheduled": (
        "Field inspection has been scheduled. The assigned officer "
        "will visit the location shortly to assess the issue."
    ),
    "Resolved": (
        "Issue has been resolved at the site. The complaint is now "
        "closed; please reach out to the department if the issue "
        "recurs."
    ),
}
_OFFICER_REMARKS_FALLBACK = "No remarks available for this complaint yet."

# Mock, department-keyed contact directory (see module docstring).
# Matched against the complaint's actual `department` field by
# keyword, so different complaint types show plausibly different
# contacts instead of one hardcoded block everywhere. Falls back to
# a generic municipal/sanitation contact when the department text
# doesn't match a known keyword.
_DEPARTMENT_CONTACT_DIRECTORY = [
    (
        "road",
        {
            "department": "Roads and Transport Department",
            "officer": "Public Works Engineer",
            "phone": "1800-419-0001",
            "email": "roads@example.gov.in",
        },
    ),
    (
        "water",
        {
            "department": "Water Resources and Supply Department",
            "officer": "Water Supply Engineer",
            "phone": "1800-419-0002",
            "email": "water@example.gov.in",
        },
    ),
    (
        "electric",
        {
            "department": "Electricity and Power Department",
            "officer": "Electrical Inspector",
            "phone": "1800-419-0003",
            "email": "electricity@example.gov.in",
        },
    ),
    (
        "health",
        {
            "department": "Public Health Department",
            "officer": "Health Inspector",
            "phone": "1800-419-0005",
            "email": "health@example.gov.in",
        },
    ),
    (
        "rural",
        {
            "department": "Rural Development Department",
            "officer": "Rural Development Officer",
            "phone": "1800-419-0006",
            "email": "ruraldev@example.gov.in",
        },
    ),
]
_DEPARTMENT_CONTACT_FALLBACK = {
    "department": "Municipal Corporation",
    "officer": "Sanitation Inspector",
    "phone": "1800-419-0004",
    "email": "municipal@example.gov.in",
}


def _get_registry() -> dict:
    """
    Returns the mock complaint tracking registry backing dict, stored
    in `st.session_state`, creating it if this is the first time this
    session has touched it.

    Returns:
        The registry dict (complaint_id -> tracked complaint record).
    """
    return st.session_state.setdefault(SESSION_STATE_REGISTRY_KEY, {})


def _estimated_resolution_text(priority: str) -> str:
    """
    Returns a display-only estimated-resolution string for a given
    priority level. See `_ESTIMATED_RESOLUTION_BY_PRIORITY` above.

    Args:
        priority: The complaint's priority (e.g. "High"). Matched
            case-insensitively; unrecognized values fall back to a
            generic message rather than guessing.

    Returns:
        A short, human-readable estimate string.
    """
    return _ESTIMATED_RESOLUTION_BY_PRIORITY.get(
        str(priority).strip().lower(), _ESTIMATED_RESOLUTION_FALLBACK
    )


def _display_stage_progress(generated_at_iso: str, current_status: str) -> list:
    """
    Maps the backend's current status (one of `STATUS_STAGES`) plus
    its raw registration timestamp onto a per-step (label, state,
    timestamp) list for the 5 `DISPLAY_STAGES` shown in the timeline.

    Because the backend has 4 stages and the timeline shows 5, the
    single backend stage "Assigned" is visually split across two
    timeline steps ("Assigned to Municipal Officer" then "Officer
    Visit Scheduled"). Rather than always marking both the instant a
    complaint reaches "Assigned", the split point is derived from how
    much of that stage's `STAGE_INTERVAL_SECONDS` window has already
    elapsed - the first half is shown as "Assigned to Municipal
    Officer" (current), the second half as "Officer Visit Scheduled"
    (current) with "Assigned to Municipal Officer" then marked done.
    This is time-based interpolation on top of the same elapsed-time
    value the backend already uses for `compute_status()` - it does
    not add any new state to the backend itself.

    Per-stage timestamps are computed the same way: stage N started
    at `generated_at + N * STAGE_INTERVAL_SECONDS` (with the
    Assigned-split sub-stage at the midpoint of its window). A
    timestamp is only included for stages already reached (state
    "done", "current", or "done-final").

    Args:
        generated_at_iso: The complaint's raw ISO-8601 registration
            timestamp, as now returned by `get_tracking_info()`. If
            missing/unparseable, states are still computed (from
            `current_status` alone) but every timestamp is `None`.
        current_status: One of `STATUS_STAGES`. If unrecognized,
            every step is returned as "upcoming" with no timestamp.

    Returns:
        A list of dicts, one per `DISPLAY_STAGES` entry in order,
        each with keys "label", "state" ("done" / "current" /
        "done-final" / "upcoming"), and "timestamp" (a `datetime` or
        `None`).
    """
    try:
        backend_index = STATUS_STAGES.index(current_status)
    except ValueError:
        backend_index = -1

    try:
        generated_at = datetime.fromisoformat(generated_at_iso)
    except (TypeError, ValueError):
        generated_at = None

    interval = STAGE_INTERVAL_SECONDS
    half_interval = interval / 2

    if backend_index < 0:
        states = ["upcoming"] * len(DISPLAY_STAGES)
    elif backend_index == 0:  # Submitted
        states = ["current", "upcoming", "upcoming", "upcoming", "upcoming"]
    elif backend_index == 1:  # Under Review
        states = ["done", "current", "upcoming", "upcoming", "upcoming"]
    elif backend_index == 2:  # Assigned - split by elapsed time within stage
        elapsed_in_stage = None
        if generated_at is not None:
            elapsed_total = max((datetime.now() - generated_at).total_seconds(), 0)
            elapsed_in_stage = elapsed_total - (backend_index * interval)
        if elapsed_in_stage is None or elapsed_in_stage < half_interval:
            states = ["done", "done", "current", "upcoming", "upcoming"]
        else:
            states = ["done", "done", "done", "current", "upcoming"]
    else:  # Resolved
        states = ["done", "done", "done", "done", "done-final"]

    stage_offsets_seconds = [0, interval, 2 * interval, 2 * interval + half_interval, 3 * interval]

    entries = []
    for label, state, offset_seconds in zip(DISPLAY_STAGES, states, stage_offsets_seconds):
        timestamp = None
        if generated_at is not None and state in ("done", "current", "done-final"):
            timestamp = generated_at + timedelta(seconds=offset_seconds)
        entries.append({"label": label, "state": state, "timestamp": timestamp})

    return entries


def _active_stage_entry(stage_entries: list) -> dict:
    """
    Returns the single stage entry the complaint is currently "at" -
    the one with state "current" or "done-final" (there is always
    exactly one, unless `current_status` was unrecognized, in which
    case every entry is "upcoming" and the first entry is returned as
    a harmless fallback). Used to pick the matching officer remark
    and the "Last Updated" timestamp.

    Args:
        stage_entries: The list returned by `_display_stage_progress()`.

    Returns:
        The active entry dict, or `stage_entries[0]` if none qualify.
    """
    for entry in stage_entries:
        if entry["state"] in ("current", "done-final"):
            return entry
    return stage_entries[0]


def _officer_remark_for_stage(stage_label: str) -> str:
    """
    Returns the display-only officer remark for a given timeline
    stage label. See `_OFFICER_REMARKS` above.
    """
    return _OFFICER_REMARKS.get(stage_label, _OFFICER_REMARKS_FALLBACK)


def _contact_for_department(department: str) -> dict:
    """
    Looks up mock department-contact info by keyword match against
    the complaint's actual `department` text. See
    `_DEPARTMENT_CONTACT_DIRECTORY` above.

    Args:
        department: The complaint's department string (e.g.
            "Sanitation and Waste Management").

    Returns:
        A dict with keys "department", "officer", "phone", "email".
        Falls back to `_DEPARTMENT_CONTACT_FALLBACK` when no keyword
        matches.
    """
    department_lower = str(department).strip().lower()
    for keyword, contact in _DEPARTMENT_CONTACT_DIRECTORY:
        if keyword in department_lower:
            return contact
    return _DEPARTMENT_CONTACT_FALLBACK


def _build_vertical_timeline_html(stage_entries: list) -> str:
    """
    Builds the HTML for a vertical progress timeline - each stage's
    label plus (once reached) the date/time it was reached, joined by
    a downward-arrow connector - generated automatically from the
    complaint's current status via `_display_stage_progress()`. The
    current stage is highlighted (teal label/marker plus a small
    "Current Stage" tag).

    Returns a string rather than calling `st.markdown()` directly, so
    the caller can splice it into one larger, single `st.markdown()`
    call alongside the rest of the result card - see
    `_render_tracking_result` for why every line here is built with
    NO leading whitespace (Streamlit's Markdown renderer otherwise
    treats 4+ leading spaces as an indented code block, and a
    <div class="gv-card"> opened in one st.markdown() call can never
    be closed in another).

    Args:
        stage_entries: The list returned by `_display_stage_progress()`.

    Returns:
        A single-line-per-tag HTML string with no leading whitespace.
    """
    row_parts = []
    for index, entry in enumerate(stage_entries):
        state = entry["state"]
        label = html.escape(entry["label"])
        timestamp = entry["timestamp"]

        current_tag = ""
        if state == "current":
            current_tag = (
                f'<span class="gv-vtimeline-current-tag">'
                f"{html.escape(TRACK_COMPLAINT_CURRENT_STAGE_TAG)}</span>"
            )

        timestamp_html = ""
        if timestamp is not None:
            timestamp_text = html.escape(timestamp.strftime("%d %b %Y \u2022 %I:%M %p"))
            timestamp_html = f'<div class="gv-vtimeline-timestamp">{timestamp_text}</div>'

        row_parts.append(
            f'<div class="gv-vtimeline-item gv-vtimeline-item-{state}">'
            '<div class="gv-vtimeline-row">'
            '<div class="gv-vtimeline-marker"></div>'
            f'<div class="gv-vtimeline-label">{label}{current_tag}</div>'
            "</div>"
            f"{timestamp_html}"
            "</div>"
        )
        if index < len(stage_entries) - 1:
            connector_state = "done" if state in ("done", "done-final") else "upcoming"
            row_parts.append(
                f'<div class="gv-vtimeline-connector gv-vtimeline-connector-{connector_state}">&#8595;</div>'
            )

    return '<div class="gv-vtimeline">' + "".join(row_parts) + "</div>"


def _render_status_card(result: dict, active_entry: dict) -> None:
    """
    Renders the primary "Complaint Status" card: Complaint ID header,
    info grid (Submission Date / Department / Priority / Estimated
    Resolution Time / Current Status / Last Updated), and - if the
    complaint has reached the final stage - a "Resolved Successfully"
    confirmation banner. Rendered as a single, flat HTML string in
    one `st.markdown()` call (see `_build_vertical_timeline_html` for
    why that matters).

    Args:
        result: The dict returned by
            `ai.utils.complaint_tracker.get_tracking_info()`. Not
            modified - the extra display fields (Estimated Resolution
            Time, Last Updated, resolved-confirmation text) are
            computed here / from `active_entry`, not fetched from the
            backend.
        active_entry: The entry from `_active_stage_entry()` for this
            result, used for the "Last Updated" timestamp.
    """
    complaint_id = html.escape(str(result.get("complaint_id", "")))
    status = str(result.get("status", ""))
    department_badge = department_badge_html(result.get("department", ""))
    tracked_date = html.escape(str(result.get("date", "")))
    priority = result.get("priority", "")
    priority_badge = priority_badge_html(priority)
    status_badge = status_badge_html(status)
    estimated_resolution = html.escape(_estimated_resolution_text(priority))

    last_updated_timestamp = active_entry.get("timestamp")
    if last_updated_timestamp is not None:
        last_updated_html = (
            f'<div>{html.escape(last_updated_timestamp.strftime("%d %b %Y"))}</div>'
            '<div class="gv-info-value-sub">'
            f'{html.escape(last_updated_timestamp.strftime("%I:%M %p"))}</div>'
        )
    else:
        last_updated_html = html.escape(tracked_date) or "&mdash;"

    info_grid_html = (
        '<div class="gv-info-grid">'
        '<div class="gv-info-item">'
        f'<div class="gv-info-label">{TRACK_COMPLAINT_DATE_LABEL}</div>'
        f'<div class="gv-info-value">{tracked_date}</div>'
        "</div>"
        '<div class="gv-info-item">'
        f'<div class="gv-info-label">{TRACK_COMPLAINT_DEPARTMENT_LABEL}</div>'
        f'<div class="gv-info-value">{department_badge}</div>'
        "</div>"
        '<div class="gv-info-item">'
        f'<div class="gv-info-label">{TRACK_COMPLAINT_PRIORITY_LABEL}</div>'
        f'<div class="gv-info-value">{priority_badge}</div>'
        "</div>"
        '<div class="gv-info-item">'
        f'<div class="gv-info-label">{TRACK_COMPLAINT_ESTIMATED_RESOLUTION_LABEL}</div>'
        f'<div class="gv-info-value">{estimated_resolution}</div>'
        "</div>"
        '<div class="gv-info-item">'
        f'<div class="gv-info-label">{TRACK_COMPLAINT_STATUS_LABEL}</div>'
        f'<div class="gv-info-value">{status_badge}</div>'
        "</div>"
        '<div class="gv-info-item">'
        f'<div class="gv-info-label">{TRACK_COMPLAINT_LAST_UPDATED_LABEL}</div>'
        f'<div class="gv-info-value">{last_updated_html}</div>'
        "</div>"
        "</div>"
    )

    resolved_html = ""
    if status == STATUS_STAGES[-1]:  # "Resolved"
        confirmation_text = (
            "Verified as resolved on "
            + datetime.now().strftime("%d %B %Y at %I:%M %p")
        )
        resolved_html = resolved_banner_html(confirmation_text)

    card_html = (
        '<div class="gv-card">'
        f"<h3>{TRACK_COMPLAINT_RESULT_CARD_TITLE}</h3>"
        f"<p><strong>{TRACK_COMPLAINT_COMPLAINT_ID_LABEL}:</strong> {complaint_id}</p>"
        f"{info_grid_html}"
        f"{resolved_html}"
        "</div>"
    )

    st.write("")
    st.markdown(card_html, unsafe_allow_html=True)


def _render_timeline_card(stage_entries: list) -> None:
    """
    Renders the "Complaint Timeline" card: title plus the vertical
    timeline built by `_build_vertical_timeline_html()`.
    """
    card_html = (
        '<div class="gv-card">'
        f"<h3>{TRACK_COMPLAINT_TIMELINE_CARD_TITLE}</h3>"
        f"{_build_vertical_timeline_html(stage_entries)}"
        "</div>"
    )
    st.write("")
    st.markdown(card_html, unsafe_allow_html=True)


def _render_remarks_card(stage_label: str) -> None:
    """
    Renders the "Officer Remarks" card: title plus the display-only
    remark text matched to the complaint's current timeline stage.
    """
    remark = html.escape(_officer_remark_for_stage(stage_label))
    card_html = (
        '<div class="gv-card">'
        f"<h3>{TRACK_COMPLAINT_REMARKS_CARD_TITLE}</h3>"
        f"<p>{remark}</p>"
        "</div>"
    )
    st.write("")
    st.markdown(card_html, unsafe_allow_html=True)


def _render_contact_card(department: str) -> None:
    """
    Renders the "Department Contact" card: mock, department-matched
    contact details (Responsible Department / Officer / Phone /
    Email), clearly labeled as mock data.
    """
    contact = _contact_for_department(department)
    info_grid_html = (
        '<div class="gv-info-grid">'
        '<div class="gv-info-item">'
        f'<div class="gv-info-label">{TRACK_COMPLAINT_CONTACT_DEPARTMENT_LABEL}</div>'
        f'<div class="gv-info-value">{html.escape(contact["department"])}</div>'
        "</div>"
        '<div class="gv-info-item">'
        f'<div class="gv-info-label">{TRACK_COMPLAINT_CONTACT_OFFICER_LABEL}</div>'
        f'<div class="gv-info-value">{html.escape(contact["officer"])}</div>'
        "</div>"
        '<div class="gv-info-item">'
        f'<div class="gv-info-label">{TRACK_COMPLAINT_CONTACT_PHONE_LABEL}</div>'
        f'<div class="gv-info-value">{html.escape(contact["phone"])}</div>'
        "</div>"
        '<div class="gv-info-item">'
        f'<div class="gv-info-label">{TRACK_COMPLAINT_CONTACT_EMAIL_LABEL}</div>'
        f'<div class="gv-info-value">{html.escape(contact["email"])}</div>'
        "</div>"
        "</div>"
    )
    card_html = (
        '<div class="gv-card">'
        f"<h3>{TRACK_COMPLAINT_CONTACT_CARD_TITLE}</h3>"
        f"{info_grid_html}"
        f'<p style="margin-top:0.9rem;margin-bottom:0;font-size:0.8rem;font-style:italic;">'
        f"{html.escape(TRACK_COMPLAINT_CONTACT_MOCK_NOTE)}</p>"
        "</div>"
    )
    st.write("")
    st.markdown(card_html, unsafe_allow_html=True)


def _render_tracking_result(result: dict) -> None:
    """
    Renders the full tracking result: the status card, the vertical
    timeline, officer remarks, and department contact - in that
    order, each its own card for a layout closer to a real grievance
    portal than one dense block.

    Args:
        result: The dict returned by
            `ai.utils.complaint_tracker.get_tracking_info()`.
    """
    status = str(result.get("status", ""))
    generated_at_iso = str(result.get("generated_at", ""))

    stage_entries = _display_stage_progress(generated_at_iso, status)
    active_entry = _active_stage_entry(stage_entries)

    _render_status_card(result, active_entry)
    _render_timeline_card(stage_entries)
    _render_remarks_card(active_entry["label"])
    _render_contact_card(result.get("department", ""))


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
    if message == TRACK_COMPLAINT_NOT_FOUND_WARNING:
        st.write("")
        render_empty_state(
            icon=TRACK_COMPLAINT_NOT_FOUND_ICON,
            title=TRACK_COMPLAINT_NOT_FOUND_TITLE,
            text=message,
        )
    elif message == TRACK_COMPLAINT_EMPTY_ID_WARNING:
        st.write("")
        render_empty_state(
            icon=TRACK_COMPLAINT_EMPTY_ID_ICON,
            title=TRACK_COMPLAINT_EMPTY_ID_TITLE,
            text=message,
        )
    elif message:
        st.warning(message)

    result = st.session_state.get(_TRACK_RESULT_KEY)
    if result:
        _render_tracking_result(result)