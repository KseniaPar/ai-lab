package com.ailab.conspect;

import com.ailab.corpus.CorpusService;
import com.ailab.course.CourseService;
import com.ailab.llm.LlmGateway;
import org.springframework.stereotype.Service;

import java.time.Instant;
import java.util.Map;
import java.util.UUID;

@Service
public class ConspectService {

    private final CourseService courses;
    private final CorpusService corpus;
    private final LlmGateway llm;
    private final ConspectRepository conspects;

    public ConspectService(
            CourseService courses,
            CorpusService corpus,
            LlmGateway llm,
            ConspectRepository conspects) {
        this.courses = courses;
        this.corpus = corpus;
        this.llm = llm;
        this.conspects = conspects;
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
        conspects.insert(new ConspectRepository.ConspectRow(id, courseId, markdown, createdAt));
        return Map.of("id", id, "courseId", courseId, "markdown", markdown, "createdAt", createdAt);
    }

    public Map<String, Object> latest(String courseId) {
        courses.requireOwned(courseId);
        return conspects.findLatestByCourse(courseId)
                .map(row -> Map.<String, Object>of(
                        "id", row.id(),
                        "courseId", row.courseId(),
                        "markdown", row.markdown(),
                        "createdAt", row.createdAt()))
                .orElseThrow(() -> new IllegalArgumentException("Конспект ещё не создан"));
    }

    public String exportMarkdown(String courseId) {
        courses.requireOwned(courseId);
        return conspects.findLatestByCourse(courseId)
                .map(ConspectRepository.ConspectRow::markdown)
                .orElseThrow(() -> new IllegalArgumentException("Конспект ещё не создан"));
    }
}
