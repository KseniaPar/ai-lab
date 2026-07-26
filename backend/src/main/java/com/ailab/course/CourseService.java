package com.ailab.course;

import com.ailab.auth.AuthContext;
import org.springframework.stereotype.Service;

import java.time.Instant;
import java.util.List;
import java.util.Map;
import java.util.UUID;

@Service
public class CourseService {

    private final CourseRepository courses;

    public CourseService(CourseRepository courses) {
        this.courses = courses;
    }

    public CourseRepository.CourseRow requireOwned(String courseId) {
        String userId = AuthContext.requireUserId();
        CourseRepository.CourseRow course = courses.findById(courseId)
                .orElseThrow(() -> new IllegalArgumentException("Курс не найден"));
        if (!course.userId().equals(userId)) {
            throw new SecurityException("Нет доступа к курсу");
        }
        return course;
    }

    public Map<String, Object> create(String title, String subject) {
        if (title == null || title.isBlank()) {
            throw new IllegalArgumentException("title обязателен");
        }
        String userId = AuthContext.requireUserId();
        String id = UUID.randomUUID().toString();
        CourseRepository.CourseRow row = new CourseRepository.CourseRow(
                id, userId, title.trim(), subject == null ? "" : subject.trim(), Instant.now().toString());
        courses.insert(row);
        return toMap(row);
    }

    public List<Map<String, Object>> listMine() {
        return courses.findByUser(AuthContext.requireUserId()).stream().map(this::toMap).toList();
    }

    public Map<String, Object> get(String courseId) {
        return toMap(requireOwned(courseId));
    }

    public void delete(String courseId) {
        requireOwned(courseId);
        courses.delete(courseId);
    }

    private Map<String, Object> toMap(CourseRepository.CourseRow row) {
        return Map.of(
                "id", row.id(),
                "title", row.title(),
                "subject", row.subject() == null ? "" : row.subject(),
                "createdAt", row.createdAt());
    }
}
