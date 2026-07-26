package com.ailab.course;

import com.ailab.auth.AuthContext;
import com.ailab.conspect.ConspectRepository;
import com.ailab.corpus.ChunkRepository;
import com.ailab.lecture.LectureRepository;
import org.springframework.stereotype.Service;

import java.time.Instant;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

@Service
public class CourseService {

    private final CourseRepository courses;
    private final LectureRepository lectures;
    private final ChunkRepository chunks;
    private final ConspectRepository conspects;

    public CourseService(
            CourseRepository courses,
            LectureRepository lectures,
            ChunkRepository chunks,
            ConspectRepository conspects) {
        this.courses = courses;
        this.lectures = lectures;
        this.chunks = chunks;
        this.conspects = conspects;
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

    public Map<String, Object> outline(String courseId) {
        CourseRepository.CourseRow course = requireOwned(courseId);
        List<Map<String, Object>> lectureMaps = lectures.findByCourse(courseId).stream()
                .map(row -> {
                    Map<String, Object> map = new LinkedHashMap<>();
                    map.put("id", row.id());
                    map.put("title", row.title());
                    map.put("sourceType", row.sourceType());
                    map.put("status", row.status());
                    map.put("createdAt", row.createdAt());
                    return map;
                })
                .toList();

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("course", Map.of(
                "id", course.id(),
                "title", course.title(),
                "subject", course.subject() == null ? "" : course.subject()));
        result.put("lectures", lectureMaps);
        result.put("materialsCount", lectures.countByCourseAndSourceType(courseId, "MATERIAL"));
        result.put("chunksCount", chunks.countByCourse(courseId));
        result.put("hasConspect", conspects.existsByCourse(courseId));
        return result;
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
