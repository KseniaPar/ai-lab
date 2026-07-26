---
name: add-course-endpoint
description: >-
  Add a course-scoped REST endpoint in Knowbase (Spring Boot).
  Use when creating GET/POST under /api/courses/{courseId}/...,
  or when the user asks for a new course API, outline, export, or stats field.
---

# Add course-scoped endpoint

## Steps

1. Read `CourseService`, `CourseAiController`, related `*Repository`, and this skill.
2. **Do not grow `CourseService`** beyond ownership/CRUD. Create `com.ailab.<feature>.<Name>Service` for aggregates.
3. Add repository methods only if new SQL is required (parameterized, text blocks). Prefer `EXISTS`/limit-1 for booleans.
4. If you introduce a feature `*Repository`, migrate that feature's `*Service` off raw `JdbcTemplate` for the same table (or inject the repo there).
5. Service method:
   - `courses.requireOwned(courseId);` first
   - Russian validation errors
   - camelCase `LinkedHashMap` / `Map` response
6. Map route on `CourseAiController` for course aggregates.
7. Ensure `ApiExceptionHandler` returns **403** for `SecurityException`.
8. Update `README.md` API table for new public routes.
9. Compile: `mvn -q -DskipTests compile` in `backend/` (Maven may be at `llm-chat-app\.tools\apache-maven-3.9.6\bin\mvn.cmd`).
10. No UI unless asked; no concept-map APIs.

## Response shape reminder

```json
{
  "course": { "id": "...", "title": "...", "subject": "..." },
  "someList": [],
  "countField": 0,
  "flagField": false
}
```
