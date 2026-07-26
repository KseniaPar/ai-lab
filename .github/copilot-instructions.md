# Copilot instructions — Knowbase

You are working in **Knowbase** (`ai-lab`): Java 17 / Spring Boot 3.4 / SQLite / JWT / OpenRouter backend and Vite vanilla JS frontend.

## Must follow
- Feature packages under `com.ailab.*`; Controller → Service → Repository
- Call `CourseService.requireOwned(courseId)` before any course-scoped read/write
- Return `Map<String, Object>` with camelCase keys; errors as `{ "error": "..." }` with Russian messages
- Keep SQL parameterized inside `@Repository` only; handle SQLite numeric nulls via `Number.longValue()` helpers
- Do not add concept-map features; do not commit secrets; do not introduce React/TypeScript unless asked
- Frontend must use `api()` from `frontend/js/api.js` for authenticated calls

## Good patterns to copy
- `CourseService.requireOwned` / `create`
- `CourseController` nested request records
- `ChunkRepository` text-block SQL + `toLong`
- `ApiExceptionHandler`
- `frontend/js/api.js`

## New course endpoint checklist
1. Ownership check 2. Input validation 3. Repository if persistence needed 4. Wire controller 5. Match existing URL style under `/api/courses/{id}/...`
