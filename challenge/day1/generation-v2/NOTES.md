# Generation v2 notes

- Compile: SUCCESS
- requireOwned: YES (via CourseOutlineService → courses.requireOwned)
- Dedicated CourseOutlineService: YES
- ConspectService migrated to ConspectRepository: YES
- SecurityException 403: YES
- README API table: YES
- hasConspect: SELECT 1 LIMIT 1
- materialsCount: in-memory filter on lecture list (sourceType MATERIAL)
