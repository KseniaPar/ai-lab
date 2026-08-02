# feature — qwen2.5-coder:7b
seconds: 115.0
eval_count: 874
prompt_eval_count: 456

---

Конечно! Давайте добавим новый эндпоинт `GET /api/courses/{courseId}/source-summary` в backend Knowbase.

### 1. Создаем новую сервисную класс для обработки запроса

Создадим новый сервисный класс `SourceSummaryService`, который будет отвечать за логику получения сводной информации о источниках курса.

```java
package com.ailab.knowbase.service;

import com.ailab.knowbase.model.Course;
import com.ailab.knowbase.repository.CourseRepository;
import com.ailab.knowbase.repository.SourceRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.stream.Collectors;

@Service
public class SourceSummaryService {

    @Autowired
    private CourseRepository courseRepository;

    @Autowired
    private SourceRepository sourceRepository;

    public SourceSummaryResponse getSourceSummary(Long courseId) {
        courses.requireOwned(courseId);

        Course course = courseRepository.findById(courseId)
                .orElseThrow(() -> new RuntimeException("Course not found"));

        List<Source> sources = sourceRepository.findByCourseId(courseId);
        long audioCount = sources.stream().filter(s -> "AUDIO".equals(s.getSourceType())).count();
        long materialCount = sources.stream().filter(s -> "MATERIAL".equals(s.getSourceType())).count();
        long readyCount = sources.stream().filter(Source::isReady).count();

        List<SourceSummary> sourceSummaries = sources.stream()
                .map(source -> new SourceSummary(
                        source.getId(),
                        source.getTitle(),
                        source.getSourceType(),
                        source.isReady()
                ))
                .collect(Collectors.toList());

        return new SourceSummaryResponse(
                course.getId(),
                course.getTitle(),
                course.getSubject(),
                sourceSummaries,
                audioCount,
                materialCount,
                readyCount
        );
    }
}
```

### 2. Создаем DTO для ответа

Создадим DTO `SourceSummary` и `SourceSummaryResponse`.

```java
package com.ailab.knowbase.model;

public record SourceSummary(Long id, String title, String sourceType, boolean status) {}
```

```java
package com.ailab.knowbase.model;

import java.util.List;

public record SourceSummaryResponse(
        Long courseId,
        String title,
        String subject,
        List<SourceSummary> sources,
        long audioCount,
        long materialCount,
        long readyCount
) {}
```

### 3. Обновляем контроллер `CourseAiController`

Добавим новый эндпоинт в контроллере `CourseAiController`.

```java
package com.ailab.knowbase.controller;

import com.ailab.knowbase.model.Course;
import com.ailab.knowbase.model.SourceSummaryResponse;
import com.ailab.knowbase.service.CourseService;
import com.ailab.knowbase.service.SourceSummaryService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/courses")
public class CourseAiController {

    @Autowired
    private CourseService courseService;

    @Autowired
    private SourceSummaryService sourceSummaryService;

    @GetMapping("/{courseId}/source-summary")
    public ResponseEntity<SourceSummaryResponse> getSourceSummary(@PathVariable Long courseId) {
        SourceSummaryResponse response = sourceSummaryService.getSourceSummary(courseId);
        return ResponseEntity.ok(response);
    }
}
```

### 4. Обновляем README API таблицу

Обновите таблицу в README файле для нового эндпоинта.

| Метод | Путь | Описание |
|-------|------|----------|
| GET   | /api/courses/{courseId}/source-summary | Получение сводной информации о источниках курса |

Теперь у вас есть новый эндпоинт `GET /api/courses/{courseId}/source-summary`, который возвращает сводную информацию о источниках курса, а также количество аудио и материалов, которые готовы.
