# backend/models

## Purpose
Defines the data structures (e.g. ORM models or dataclasses) that
represent core entities: Complaint, Citizen, Scheme, Status.

## Expected Responsibilities (future)
- Shared data models/schemas used across `backend/services` and
  `backend/database`.
- Validation rules tied to each entity.

## Future Integration
Imported by `backend/services` and `backend/database`. May also be
reused for API request/response validation in `backend/api`.

No implementation exists yet.
