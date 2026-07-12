# ai/llm

## Purpose

Houses the large language model integrations used for GramVaani AI.

**Implemented today:**

- **Complaint generation** (`complaint_generator.py`) - converts a
  Whisper transcript into a structured, professional complaint
  record using Google Gemini.

**Not yet implemented (future scope, out of scope for this task):**

- Government scheme recommendation.
- General conversational assistance.

## Files

- `complaint_generator.py` — configures and caches the Gemini
  client, sends the prompt, and validates/parses the JSON response.
  Exposes `generate_complaint(transcript: str) -> dict`.
- `prompts.py` — the prompt template used to instruct Gemini; kept
  separate from `complaint_generator.py` so prompt wording can be
  iterated on independently of the API-calling logic.

## Expected Input

`generate_complaint()` takes a single string: the transcript produced
by `ai/speech/speech_service.py`.

## Expected Output

A dict with exactly these keys:

```json
{
  "complaint_type": "",
  "department": "",
  "priority": "",
  "summary": "",
  "formal_complaint": ""
}
```

## Configuration

Requires a `GEMINI_API_KEY` environment variable, read from a local
`.env` file (via `python-dotenv`). Optionally override the model
with `GEMINI_MODEL` (defaults to `gemini-1.5-flash`).

## Error Handling

- Empty/blank transcript → raises `ValueError`.
- Missing API key, API/network failure, empty response, invalid
  JSON, or JSON missing required fields → raises
  `ComplaintGenerationError`.

Both are designed to be caught by the calling UI layer and shown as
a friendly warning/error rather than a stack trace.

## Future Integration

Called today from `frontend/pages/file_complaint.py`'s "Generate
Complaint" button, using the transcript already stored after the
Speech-to-Text step. Scheme recommendation will be added to this
folder later as a separate function/file - it is intentionally not
part of this implementation.
