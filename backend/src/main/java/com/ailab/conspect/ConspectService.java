package com.ailab.conspect;

import com.ailab.corpus.CorpusService;
import com.ailab.course.CourseService;
import com.ailab.llm.LlmGateway;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;

import java.time.Instant;
import java.util.List;
import java.util.Map;
import java.util.UUID;

@Service
public class ConspectService {

    private final CourseService courses;
    private final CorpusService corpus;
    private final LlmGateway llm;
    private final JdbcTemplate jdbc;

    public ConspectService(
            CourseService courses,
            CorpusService corpus,
            LlmGateway llm,
            JdbcTemplate jdbc) {
        this.courses = courses;
        this.corpus = corpus;
        this.llm = llm;
        this.jdbc = jdbc;
    }

    public Map<String, Object> generate(String courseId) {
        var course = courses.requireOwned(courseId);
        String preview = corpus.corpusPreview(courseId, 12_000);
        if (preview.isBlank()) {
            throw new IllegalStateException("Корпус пуст — загрузите лекции и дождитесь READY");
        }
        String system = """
                Ты помощник для подготовки к экзамену. Составь качественный конспект курса на русском.
                Структура: краткое введение, основные темы с подпунктами, ключевые термины, возможные экзаменационные акценты.
                Опирайся только на предоставленный корпус. Markdown.
                """;
        String user = "Курс: " + course.title() + " (" + course.subject() + ")\n\nКорпус:\n" + preview;
        String markdown = llm.complete(system, user);
        String id = UUID.randomUUID().toString();
        String createdAt = Instant.now().toString();
        jdbc.update(
                "INSERT INTO conspects(id, course_id, markdown, created_at) VALUES (?,?,?,?)",
                id, courseId, markdown, createdAt);
        return Map.of("id", id, "courseId", courseId, "markdown", markdown, "createdAt", createdAt);
    }

    public Map<String, Object> latest(String courseId) {
        courses.requireOwned(courseId);
        List<Map<String, Object>> rows = jdbc.query(
                """
                SELECT id, course_id, markdown, created_at FROM conspects
                WHERE course_id = ? ORDER BY created_at DESC LIMIT 1
                """,
                (rs, i) -> Map.of(
                        "id", rs.getString("id"),
                        "courseId", rs.getString("course_id"),
                        "markdown", rs.getString("markdown"),
                        "createdAt", rs.getString("created_at")),
                courseId);
        if (rows.isEmpty()) {
            throw new IllegalArgumentException("Конспект ещё не создан");
        }
        return rows.get(0);
    }
}
