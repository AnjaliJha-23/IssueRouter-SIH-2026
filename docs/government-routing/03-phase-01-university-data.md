# Phase 1: University Database

## Objective
Establish a reliable data foundation for the Jharkhand university ecosystem to enable smart challenge routing. This phase adds necessary university attributes and imports the real dataset.

## Scope
- Expand the existing `Organization` model to store university-specific fields.
- Update Pydantic schemas.
- Implement an idempotent CSV seed script to ingest data from `docs/Jharkhand universities list with domains.csv`.
- Expose basic CRUD endpoints for universities.

## Files Modified
- `backend/db/models.py`: Added `district`, `research_domains`, `research_specializations`, `research_output`, `status`, `created_at`, `updated_at` to the `Organization` model.
- `backend/db/schemas.py`: Updated `OrganizationOut` to include the new fields. Added `OrganizationCreate` and `OrganizationUpdate`.
- `backend/main.py`: Registered the new `universities` router.

## Files Created
- `backend/seed_universities.py`: Idempotent script that reads the provided CSV, maps it to the database schema, and upserts universities. It relies on the `University Name` for deduplication.
- `backend/api/universities.py`: Defines GET `/`, GET `/{id}`, POST `/`, PUT `/{id}`, PATCH `/{id}/status` endpoints specifically for `type="University"`.

## Database Changes
- Altered the `organizations` table in `issueRouter.db` to add columns: `district` (VARCHAR), `research_domains` (VARCHAR), `research_specializations` (VARCHAR), `research_output` (TEXT), `status` (VARCHAR, default 'ACTIVE'), `created_at` (DATETIME), `updated_at` (DATETIME).

## API Changes
- New Router: `/api/universities/`
  - `GET /api/universities/`: List all universities with optional filtering by status, domain, district, and search.
  - `GET /api/universities/{org_id}`: Retrieve a single university.
  - `POST /api/universities/`: Manually add a university.
  - `PUT /api/universities/{org_id}`: Edit university details.
  - `PATCH /api/universities/{org_id}/status`: Toggle ACTIVE/INACTIVE status.

## Design Decisions
- Reused the existing `Organization` model instead of creating a separate `University` table to avoid breaking the existing user-organization and match relationships. We filter by `type="University"` at the API level.
- District was inferred directly from the location string in the CSV to maintain simplicity, as the city/district maps 1:1 in this specific dataset.
- Adopted the idempotent upsert approach for `seed_universities.py` so that it doesn't wipe existing mock organizations and can be safely re-run if the CSV updates.

## Test Cases
- **Test 1**: Verify `seed_universities.py` runs successfully. (Passed - inserted 34 universities).
- **Test 2**: Run `seed_universities.py` a second time to verify idempotency. (Passed - script correctly updated 34 rows rather than creating duplicates).

## Regression Checks
- Existing routing mock in `/api/challenges/{id}/route` still works because we only added non-nullable fields.
- The base `Organization` model didn't drop previous fields (`id`, `name`, `type`, `location`), ensuring backward compatibility with `api/smart_router.py`.

## Next Phase
**Phase 2 — University Directory UI**: Implement the government-facing interface to view, filter, and manage these imported universities.
