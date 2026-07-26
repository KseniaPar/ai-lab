## Cause
`AskService.formatTimestamp` used `String.format("%d:%d", mm, ss)`, which does not zero-pad seconds. For 65000 ms that produced `1:5` instead of the expected citation label `1:05`.

## Fix
Changed the format string in `backend/src/main/java/com/ailab/qa/AskService.java` to `"%d:%02d"` so seconds are always two digits while minutes stay unpadded.

## Verification
- Commands run:
  - `mvn -q "-Dtest=CitationTimestampTest,ChunkerTest" test` (backend/)
  - `mvn -q test` (backend/)
- Results: both exited 0; `CitationTimestampTest` and full suite passed.

## Blast radius
- Only citation labels built in `AskService` (Q&A prompt / response citations) use this private helper; no other callers of `formatTimestamp` or `%d:%d` timestamp formatting elsewhere.
- Residual risk: low — minutes still use `%d` (as tests expect: `0:05`, `1:05`, `12:00`); null `startMs` still returns null.
