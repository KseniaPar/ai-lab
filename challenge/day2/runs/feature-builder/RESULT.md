## Delivered
`GET /api/courses/{courseId}/conspect/export` — ownership via `requireOwned`; missing conspect → `400` `"Конспект ещё не создан"`; body = latest markdown; `Content-Type: text/markdown; charset=UTF-8`; `Content-Disposition: attachment; filename="conspect-{courseId}.md"`. Thin «Скачать Markdown» button on `course.html` (fetch + Bearer).

## Files
- created: `challenge/day2/runs/feature-builder/RESULT.md`
- modified: `backend/src/main/java/com/ailab/conspect/ConspectService.java`, `backend/src/main/java/com/ailab/course/CourseAiController.java`, `README.md`, `frontend/course.html`

## Verification
- compile/tests: `mvn -q -DskipTests compile` in `backend/` — success (exit 0)

## Notes
- Reused existing `ConspectRepository.findLatestByCourse`; no new SQL/repo.
- `SecurityException` → 403 already handled in `ApiExceptionHandler`.
- Download UI uses `fetch` (not `api()`) because response is raw Markdown, not JSON.
