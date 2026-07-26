# Day 3 — Level 1 report

## Goal

Add fast unit tests for under-tested business-logic modules (no live OpenRouter / network).

## Modules covered

| Module | Test class | What was asserted |
|--------|------------|-------------------|
| `auth.JwtService` | `JwtServiceTest` | create/parse round-trip, short-secret padding, tampered & wrong-secret rejection, JWT shape |
| `auth.AuthService` | `AuthServiceTest` | register validation, duplicate user, login success/failure; in-memory `UserRepository` fake + real `JwtService` |
| `course.CourseOutlineService` | `CourseOutlineServiceTest` | materials count, null subject → `""`, empty course aggregates (`chunksCount`, `hasConspect`) |
| `common.ApiExceptionHandler` | `ApiExceptionHandlerTest` | 400 / 409 / 403 / 500 mapping and null-message fallback |

## New test files

- `backend/src/test/java/com/ailab/auth/JwtServiceTest.java`
- `backend/src/test/java/com/ailab/auth/AuthServiceTest.java`
- `backend/src/test/java/com/ailab/course/CourseOutlineServiceTest.java`
- `backend/src/test/java/com/ailab/common/ApiExceptionHandlerTest.java`

## Pre-existing tests (unchanged)

- `ChunkerTest` — plain text chunking
- `CitationTimestampTest` — `AskService.formatTimestamp`

## Maven result

```
mvn test   (backend/)
Tests run: 22, Failures: 0, Errors: 0, Skipped: 0
BUILD SUCCESS
```

All tests passed (new + existing). No production code changes required.

## Gaps left

Still light or no dedicated unit coverage for:

- `CourseService.requireOwned` / CRUD (needs `AuthContext` + repo)
- `CorpusService`, `ConspectService`, `AskService` (beyond timestamp) — LLM-heavy
- `LectureService` / `TranscriptionJobService` / `AudioChunker` (ffmpeg / IO)
- Repository SQL (`ChunkRepository`, `ConspectRepository`, …) — better as SQLite integration tests
- Controllers / security filter wiring
