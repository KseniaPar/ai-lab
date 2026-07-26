# Knowbase (ai-lab)

Exam-prep knowledge platform. Audio → STT → corpus → conspect → cited Q&A. **No concept map.**

## Stack
- Backend: Java 17, Spring Boot 3.4, SQLite (`JdbcTemplate`), JWT, OpenRouter
- Frontend: Vite + vanilla JS
- Ports: 8081 (API), 5173 (UI)

## Layout
```
backend/src/main/java/com/ailab/{auth,course,lecture,corpus,conspect,qa,stt,llm,db,common,stats,config}/
frontend/{login,courses,course}.html  js/api.js  css/app.css
.cursor/rules/*.mdc   .cursor/skills/
```

## Conventions
- Package-by-feature; Controller → Service → Repository
- Nested `record` DTOs; camelCase JSON maps
- Always `courses.requireOwned(courseId)` for course-scoped ops
- Russian validation/error strings; `{ "error": "..." }`
- Parameterized SQL only in `@Repository`; SQLite `toLong(getObject)` for nullable longs
- Secrets in `application-local.yml` (gitignored) or env

## Prefer
Constructor injection, thin controllers, reuse `LlmGateway` / `CorpusService` / `api()` helper.

## Avoid
Field injection, SQL in controllers, skipping ownership, committing keys, React/TS, concept-map features, `console.log` of tokens.

## Agent notes
Read `.cursor/rules/` and skill `add-course-endpoint` before adding APIs. Project rules override global user prefs on conflicts.
