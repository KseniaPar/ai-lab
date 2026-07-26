# Generation v1 notes

- Compile: SUCCESS
- requireOwned: YES
- SecurityException 403: YES (added handler)
- README API table: NOT updated
- Unit test: NOT added
- Placement: outline() on CourseService (injected LectureRepository, ChunkRepository, ConspectRepository) — CourseService became an aggregate hub
- ConspectRepository created but ConspectService still uses JdbcTemplate directly (dual access paths)
- materialsCount via countByCourseAndSourceType — good
- LinkedHashMap for stable key order — good
- No skill mention of preferring dedicated *Service for aggregates vs bloating CourseService
