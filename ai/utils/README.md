# ai/utils

## Purpose
Small, self-contained utilities that support the complaint pipeline
but aren't AI model calls themselves. Each file is independent - they
don't import each other.

## Files

- `complaint_id.py` — `generate_complaint_id() -> str`. Produces IDs
  like `GV-20260713-00001` (prefix + date + 5 random digits).
- `complaint_tracker.py` — mock, session-only status tracking. No
  database, no authentication. `register_complaint()` /
  `get_tracking_info()` operate on a plain dict the caller owns (via
  `st.session_state[SESSION_STATE_REGISTRY_KEY]`). Status
  (`Submitted -> Under Review -> Assigned -> Resolved`) is derived
  automatically from elapsed time since registration.
- `pdf_generator.py` — `generate_complaint_pdf(complaint, schemes) -> bytes`.
  Renders a formatted PDF report (via `reportlab`) containing the
  complaint details and recommended schemes, for the "Download
  Complaint" button.

## Configuration
None - entirely offline, no external API calls, no environment
variables.

## Used by
All three are called from `frontend/pages/file_complaint.py` right
after a complaint is generated. `complaint_tracker`'s registry is
also read independently by `frontend/pages/track_complaint.py` (to
look up status) and `frontend/pages/home.py` (to show live session
stats) - each just reads the same `st.session_state` key rather than
calling back into `file_complaint.py`.
