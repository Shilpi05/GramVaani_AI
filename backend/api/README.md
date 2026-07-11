# backend/api

## Purpose
Exposes GramVaani AI's backend functionality over HTTP (e.g. a
FastAPI/Flask layer), for future scenarios where the frontend is
decoupled from the backend, or third parties need programmatic access.

## Expected Responsibilities (future)
- Route definitions (e.g. `POST /complaints`, `GET /schemes`).
- Request/response validation.
- Authentication/authorization (future scope).

## Future Integration
Wraps `backend/services`. The current Streamlit frontend does not
require this layer yet, since it can call `backend/services` directly
in-process - this exists for future decoupling.

No implementation exists yet.
