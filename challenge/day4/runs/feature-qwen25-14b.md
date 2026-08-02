# feature — qwen2.5:14b
seconds: 438.4
eval_count: 970
prompt_eval_count: 456

---

Для добавления нового endpoint `/api/courses/{courseId}/source-summary` в бэкенд Knowbase, нужно выполнить следующие шаги:

1. Создать новый сервис для обработки запросов к источнику.
2. Обновить контроллер `CourseAiController`.
3. Добавить необходимые методы и классы.

Вот полный код новых/изменённых Java-файлов:

### 1. Создание нового сервиса

Создадим новый сервис `SourceService` для обработки запросов к источникам.

**com.ailab.service.SourceService.java:**

```java
package com.ailab.service;

import com.ailab.dto.CourseDto;
import com.ailab.dto.SourceSummaryDto;
import com.ailab.repository.CourseRepository;
import com.ailab.repository.SourceRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Map;

@Service
public class SourceService {

    @Autowired
    private CourseRepository courseRepository;

    @Autowired
    private SourceRepository sourceRepository;

    public SourceSummaryDto getSourceSummary(Long courseId) {
        // Проверка на владение курсом
        courseRepository.requireOwned(courseId);

        List<Map<String, Object>> sources = sourceRepository.findByCourseId(courseId);
        int audioCount = (int) sources.stream().filter(s -> "AUDIO".equals(s.get("source_type"))).count();
        int materialCount = (int) sources.stream().filter(s -> "MATERIAL".equals(s.get("source_type"))).count();
        int readyCount = (int) sources.stream().filter(s -> "READY".equals(s.get("status"))).count();

        return new SourceSummaryDto(
                courseId,
                courseRepository.findById(courseId).orElseThrow().getTitle(),
                courseRepository.findById(courseId).orElseThrow().getSubject(),
                sources,
                audioCount,
                materialCount,
                readyCount
        );
    }
}
```

### 2. Обновление контроллера `CourseAiController`

Обновим контроллер `CourseAiController` для обработки нового endpoint.

**com.ailab.controller.CourseAiController.java:**

```java
package com.ailab.controller;

import com.ailab.dto.SourceSummaryDto;
import com.ailab.service.CourseService;
import com.ailab.service.SourceService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/courses")
public class CourseAiController {

    @Autowired
    private SourceService sourceService;

    @GetMapping("/{courseId}/source-summary")
    @PreAuthorize("hasRole('USER')")
    public ResponseEntity<SourceSummaryDto> getSourceSummary(@PathVariable Long courseId) {
        return ResponseEntity.ok(sourceService.getSourceSummary(courseId));
    }
}
```

### 3. Обновление репозитория `SourceRepository`

Добавим метод для получения источников по курсу.

**com.ailab.repository.SourceRepository.java:**

```java
package com.ailab.repository;

import com.ailab.dto.CourseDto;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Map;

@Repository
public class SourceRepository {

    @Autowired
    private JdbcTemplate jdbcTemplate;

    public List<Map<String, Object>> findByCourseId(Long courseId) {
        String sql = "SELECT * FROM sources WHERE course_id = ?";
        return jdbcTemplate.queryForList(sql, courseId);
    }
}
```

### 4. Обновление DTO

Создадим новый DTO `SourceSummaryDto` для передачи данных.

**com.ailab.dto.SourceSummaryDto.java:**

```java
package com.ailab.dto;

import java.util.List;
import java.util.Map;

public record SourceSummaryDto(
        Long courseId,
        String title,
        String subject,
        List<Map<String, Object>> sources,
        int audioCount,
        int materialCount,
        int readyCount
) {}
```

### 5. Обновление README

Обновим таблицу API в `README.md`:

| Endpoint | HTTP Method | Description |
|----------|------------|-------------|
| /api/courses/{courseId}/source-summary | GET | Получение сводки источников курса |

Теперь новый endpoint `/api/courses/{courseId}/source-summary` готов к использованию.
