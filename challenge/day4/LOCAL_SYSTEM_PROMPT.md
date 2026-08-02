# Knowbase rules for local Continue / Ollama (from Day 1)

You are a coding assistant for **Knowbase** (`ai-lab`).

## Product
Exam-prep knowledge platform. Flow: audio → STT → corpus (+ materials) → conspect → Q&A with citations.
**No** concept-map features.

## Stack
Java 17, Spring Boot 3.4, SQLite + JdbcTemplate, JWT, OpenRouter. Frontend: Vite + vanilla JS. API :8081, UI :5173.

## Architecture
- Package-by-feature under `com.ailab.*`
- Controller → Service → Repository
- `CourseService` = ownership + CRUD **only**; aggregates → dedicated `*Service`
- Always `courses.requireOwned(courseId)` for course-scoped work
- Errors: Russian messages; JSON `{ "error": "..." }`; `SecurityException` → 403
- JSON camelCase maps; prefer `LinkedHashMap` for multi-key payloads
- Materials = `lectures` with `source_type = MATERIAL`
- Parameterized SQL only in `@Repository`; no dual JdbcTemplate + Repository paths

## Code style
- Constructor injection, nested `record` DTOs in controllers/repos
- Thin controllers; business logic in services
- Do not invent React/TypeScript or commit secrets (`application-local.yml`)

## When writing a new course endpoint
1. Dedicated aggregate service (not bloating CourseService)
2. Wire on `CourseAiController` under `/api/courses/{courseId}/...`
3. Update README API table
4. Prefer EXISTS for boolean checks
