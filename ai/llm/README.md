# ai/llm

## Purpose
Houses the large language model integrations used for scheme
recommendation, complaint summarization/categorization, and any
conversational assistance features.

## Expected Input
- Structured citizen profile data (for scheme matching) or raw
  complaint text (for summarization/categorization).

## Expected Output
- Ranked list of recommended schemes with eligibility rationale, or
- A structured summary/category label for a complaint.

## Future Integration
Will be called from `frontend/pages/scheme_finder.py` for
recommendations and potentially from `frontend/pages/file_complaint.py`
for auto-categorizing complaints before they reach `backend/services`.

No implementation exists yet.
