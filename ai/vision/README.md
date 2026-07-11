# ai/vision

## Purpose
Analyzes citizen-uploaded photos of civic issues (potholes, garbage,
broken streetlights, etc.) to classify issue type and severity, and
optionally detect duplicate/spam submissions.

## Expected Input
- One or more image files (e.g. `.jpg`, `.png`) uploaded via the
  "Upload Evidence" section of the File Complaint page.

## Expected Output
- Predicted issue category (e.g. "road damage", "sanitation").
- Confidence score.
- Optional flags (e.g. blurry image, duplicate detected).

## Future Integration
Will be called from `frontend/pages/file_complaint.py` after image
upload, with results attached to the complaint sent to
`backend/services` for persistence.

No implementation exists yet.
