# backend/services

## Purpose
Business logic layer that orchestrates operations such as filing a
complaint, matching schemes, or updating complaint status. This is
the layer the frontend will call into - it should never be called
directly from `frontend/`.

## Expected Responsibilities (future)
- Coordinate between `ai/`, `backend/database`, and `backend/models`.
- Enforce business rules (e.g. duplicate complaint detection,
  eligibility validation).

## Future Integration
`frontend/pages/file_complaint.py`, `scheme_finder.py`, and
`track_complaint.py` will call functions exposed here instead of
touching the database or AI modules directly.

No implementation exists yet.
