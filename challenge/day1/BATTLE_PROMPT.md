Добавь GET /api/courses/{courseId}/outline в backend Knowbase.

Контракт ответа (JSON):
- course: { id, title, subject }
- lectures: массив объектов { id, title, sourceType, status, createdAt }, все лекции курса по createdAt
- materialsCount: количество лекций/материалов с sourceType MATERIAL
- chunksCount: число чанков корпуса курса
- hasConspect: true если для курса есть хотя бы один conspect

Требования: только backend, без UI; проверка владельца курса; стиль и паттерны этого репозитория; после изменений выполни `mvn -q -DskipTests compile` в backend и поправь, если не компилируется. Один проход — без уточняющих вопросов.
