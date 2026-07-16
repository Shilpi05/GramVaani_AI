# ai/llm

## Purpose

Houses the large language model integration used for GramVaani AI.

**Implemented today:**

- **Complaint generation** (`complaint_generator.py`) - converts a
  Whisper transcript into a structured, professional complaint
  record using Groq's chat completions API.

**Not implemented here (lives elsewhere):**

- Government scheme recommendation - see `ai/schemes/`.
- Complaint ID generation, PDF export, and mock status tracking -
  see `ai/utils/`.

## Files

- `complaint_generator.py` — configures and caches the Groq client,
  sends the prompt, and validates/parses the JSON response. Tries
  `llama-3.3-70b-versatile` first, automatically falling back to
  `llama-3.1-8b-instant` if the primary model is unavailable or the
  call fails. Exposes `generate_complaint(transcript: str) -> dict`.
- `prompts.py` — the prompt template used to instruct the model, kept
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

The caller (`frontend/pages/file_complaint.py`) attaches two more
keys - `complaint_id` and `generated_date` - after this function
returns; they are not part of this module's own output.

## Configuration

Requires a `GROQ_API_KEY` environment variable, read from a local
`.env` file (via `python-dotenv`). Optionally override the model with
`GROQ_MODEL` / `GROQ_FALLBACK_MODEL`, and tune `GROQ_TIMEOUT_SECONDS`
/ `GROQ_RETRY_ATTEMPTS`. See `.env.example` for the full list.

## Error Handling

- Empty/blank transcript → raises `ValueError`.
- Missing API key, API/network failure, timeout, empty response,
  invalid JSON, or JSON missing required fields (on both the primary
  and fallback model) → raises `ComplaintGenerationError`.

Both are designed to be caught by the calling UI layer and shown as
a friendly warning/error rather than a stack trace.

## Used by

`frontend/pages/file_complaint.py`'s "Generate Complaint" button,
using the transcript already stored after the Speech-to-Text step.
