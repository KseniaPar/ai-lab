# Day 4 bench prompts — same shape as Day 1 / Day 2 cloud tasks

## FEATURE (Day 1 style)

Добавь GET /api/courses/{courseId}/source-summary в backend Knowbase.

Контракт JSON:
- course: { id, title, subject }
- sources: массив { id, title, sourceType, status } по лекциям/материалам курса
- audioCount: число sourceType AUDIO
- materialCount: число sourceType MATERIAL
- readyCount: число status READY

Только backend, ownership через requireOwned, стиль проекта (dedicated service, не раздувать CourseService).
Выдай полный код новых/изменённых Java-файлов.

## AGENT_BUGFIX (Day 2 style)

Баг: CitationTimestampTest ожидает "1:05" для 65000ms, но formatTimestamp в AskService печатает "1:5".
Найди причину, предложи минимальный фикс (diff), что проверить через mvn test.
Формат: Cause / Fix / Verification / Blast radius.
