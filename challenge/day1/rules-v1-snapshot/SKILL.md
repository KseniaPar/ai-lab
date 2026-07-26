---
name: add-course-endpoint
description: >-
  Add a course-scoped REST endpoint in Knowbase (Spring Boot).
  Use when creating GET/POST under /api/courses/{courseId}/...,
  or when the user asks for a new course API, outline, export, or stats field.
---

# Add course-scoped endpoint

## Steps

1. Read `CourseService`, `CourseAiController` / feature controller, and related `*Repository`.
2. Add repository methods only if new SQL is required (parameterized, text blocks).
3. Implement service method:
   - first line after entry: `courses.requireOwned(courseId);`
   - validate inputs; Russian `IllegalArgumentException` messages
   - return camelCase `Map` / `List<Map>`
4. Expose on the appropriate `@RestController` (prefer extending `CourseAiController` for AI/read aggregates).
5. Handle `SecurityException` consistently (403) if touching `ApiExceptionHandler`.
6. Compile: `mvn -q -DskipTests compile` in `backend/`.
7. Do **not** add UI unless asked; do **not** invent concept-map APIs.

## Response shape reminder

```json
{
  "course": { "id": "...", "title": "...", "subject": "..." },
  "someList": [],
  "countField": 0,
  "flagField": false
}
```
