"""
complaint_tracker.py
-----------------------
Mock Complaint Tracking system for GramVaani AI.

There is NO database and NO authentication. Complaints are tracked
entirely in Streamlit's `st.session_state` for the lifetime of the
browser session/tab - once the session ends (browser closed, server
restarted), tracking data is gone. This is intentional: it's a mock
system for demo/prototype purposes, not a persistence layer.

Every complaint moves through exactly four fixed stages, in order:

    Submitted -> Under Review -> Assigned -> Resolved

Since there is no real backend to advance a complaint's status, the
current stage is derived automatically from how much wall-clock time
has passed since the complaint was generated (a new complaint starts
as "Submitted" and automatically progresses to the next stage every
`STAGE_INTERVAL_SECONDS` seconds, capping at "Resolved"). This gives
a citizen tracking their complaint a believable, live-feeling status
without requiring any server-side workflow engine.

This module owns only the tracking *business logic* - registration,
lookup, and status computation. It intentionally has no Streamlit
imports of its own; the page that uses it
(`frontend/pages/track_complaint.py`) is responsible for owning the
actual `st.session_state` dict and passing it in as `registry`.

Public API:
    STATUS_STAGES               - the four ordered status names
    SESSION_STATE_REGISTRY_KEY  - the st.session_state key the page
                                   should store the registry dict under
    register_complaint(registry, complaint) -> None
    get_tracking_info(registry, complaint_id) -> Optional[Dict[str, str]]
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, TypedDict

# ----------------------------------------------------------------------
# Logging
# ----------------------------------------------------------------------
# A dedicated, namespaced logger, consistent with the rest of the
# `ai` package (see ai/llm/complaint_generator.py, ai/schemes/
# scheme_recommender.py, ai/utils/complaint_id.py,
# ai/utils/pdf_generator.py).
logger = logging.getLogger("gramvaani.ai.utils.complaint_tracker")
if not logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(
        logging.Formatter("[%(asctime)s] %(levelname)s %(name)s: %(message)s")
    )
    logger.addHandler(_handler)
    logger.setLevel(logging.INFO)

# ----------------------------------------------------------------------
# Status stages (fixed, ordered, non-configurable pipeline)
# ----------------------------------------------------------------------
STATUS_STAGES: List[str] = ["Submitted", "Under Review", "Assigned", "Resolved"]

# How long (in seconds) a complaint spends in each stage before
# automatically advancing to the next one. Deliberately short so the
# mock progression is visible within a normal demo/testing session.
STAGE_INTERVAL_SECONDS: int = 25

# The st.session_state key the Track Complaint page should use to
# store the registry dict (complaint_id -> TrackedComplaint).
SESSION_STATE_REGISTRY_KEY: str = "gv_complaint_registry"


class TrackedComplaint(TypedDict):
    """The record stored per complaint_id in the tracking registry."""

    complaint_type: str
    department: str
    priority: str
    generated_date: str
    generated_at: str  # ISO-8601 datetime string, used to derive status


def register_complaint(
    registry: Dict[str, TrackedComplaint], complaint: Dict[str, Any]
) -> None:
    """
    Registers a freshly generated complaint in the mock tracking
    registry, so it can later be looked up by Complaint ID on the
    Track Complaint page. Safe to call multiple times for the same
    complaint_id - re-registering simply resets its tracking clock.

    Args:
        registry: The dict backing the tracker (expected to be
            `st.session_state[SESSION_STATE_REGISTRY_KEY]`).
        complaint: The complaint dict, expected to contain
            "complaint_id", "complaint_type", "department",
            "priority", and "generated_date".
    """
    complaint_id = str(complaint.get("complaint_id", "")).strip()
    if not complaint_id:
        logger.warning(
            "Cannot register complaint for tracking - missing complaint_id."
        )
        return

    registry[complaint_id] = {
        "complaint_type": str(complaint.get("complaint_type", "")),
        "department": str(complaint.get("department", "")),
        "priority": str(complaint.get("priority", "")),
        "generated_date": str(complaint.get("generated_date", "")),
        "generated_at": datetime.now().isoformat(),
    }
    logger.info("Registered complaint '%s' for mock tracking.", complaint_id)


def compute_status(generated_at_iso: str) -> str:
    """
    Derives the current mock status of a complaint from how long ago
    it was registered.

    Args:
        generated_at_iso: An ISO-8601 datetime string (as stored by
            `register_complaint`).

    Returns:
        One of `STATUS_STAGES`. Falls back to the first stage
        ("Submitted") if the timestamp is missing or unparseable.
    """
    try:
        generated_at = datetime.fromisoformat(generated_at_iso)
    except (TypeError, ValueError):
        return STATUS_STAGES[0]

    elapsed_seconds = max((datetime.now() - generated_at).total_seconds(), 0)
    stage_index = min(
        int(elapsed_seconds // STAGE_INTERVAL_SECONDS), len(STATUS_STAGES) - 1
    )
    return STATUS_STAGES[stage_index]


def get_tracking_info(
    registry: Dict[str, TrackedComplaint], complaint_id: str
) -> Optional[Dict[str, str]]:
    """
    Looks up a complaint by ID and returns its current tracking
    status alongside its department, date, priority, and raw
    registration timestamp.

    Args:
        registry: The dict backing the tracker (expected to be
            `st.session_state[SESSION_STATE_REGISTRY_KEY]`).
        complaint_id: The Complaint ID the citizen entered, e.g.
            "GV-20260713-00001". Leading/trailing whitespace is
            stripped before lookup.

    Returns:
        A dict with keys "complaint_id", "status", "department",
        "date", "priority", "complaint_type", "generated_at" if
        found, or None if no complaint with that ID has been
        registered in this session. "generated_at" is the raw
        ISO-8601 string already stored by `register_complaint()` -
        exposed here (previously computed internally but not
        returned) purely so callers can derive presentational detail
        such as per-stage timestamps; it does not change how status
        is computed.
    """
    normalized_id = complaint_id.strip()
    record = registry.get(normalized_id)

    if record is None:
        logger.info(
            "No tracked complaint found for Complaint ID '%s'.", normalized_id
        )
        return None

    status = compute_status(record.get("generated_at", ""))
    logger.info(
        "Tracked complaint '%s' - current status: '%s'.", normalized_id, status
    )

    return {
        "complaint_id": normalized_id,
        "status": status,
        "department": record.get("department", ""),
        "date": record.get("generated_date", ""),
        "priority": record.get("priority", ""),
        "complaint_type": record.get("complaint_type", ""),
        "generated_at": record.get("generated_at", ""),
    }