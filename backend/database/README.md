# backend/database

## Purpose
Owns database connection setup, schema/migrations, and low-level
data access (queries/writes) for complaints, schemes, and users.

## Expected Responsibilities (future)
- Database connection/session management.
- Schema definitions and migrations.
- CRUD operations used internally by `backend/services`.

## Future Integration
Only `backend/services` should import from this folder. Frontend
and AI modules should never query the database directly.

No implementation exists yet.
