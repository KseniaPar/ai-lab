package com.ailab.qa;

import com.ailab.corpus.ChunkRepository;
import com.ailab.corpus.CorpusService;
import com.ailab.course.CourseService;
import com.ailab.llm.LlmGateway;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;

import java.time.Instant;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

@Service
public class AskService {

    private final CourseService courses;
    private final CorpusService corpus;
    private final LlmGateway llm;
    private final JdbcTemplate jdbc;
    private final ObjectMapper objectMapper;

    public AskService(
            CourseService courses,
            CorpusService corpus,
            LlmGateway llm,
            JdbcTemplate jdbc,
            ObjectMapper objectMapper) {
        this.courses = courses;
        this.corpus = corpus;
        this.llm = llm;
        this.jdbc = jdbc;
        this.objectMapper = objectMapper;
    }

    public Map<String, Object> ask(String courseId, String question) {
        courses.requireOwned(courseId);
        if (question == null || question.isBlank()) {
            throw new IllegalArgumentException("question обязателен");
        }
        List<ChunkRepository.ChunkRow> retrieved = corpus.retrieve(courseId, question);
        if (retrieved.isEmpty()) {
            throw new IllegalStateException("Корпус пуст — загрузите лекции");
        }

        StringBuilder context = new StringBuilder();
        List<Map<String, Object>> citations = new ArrayList<>();
        int idx = 1;
        for (ChunkRepository.ChunkRow chunk : retrieved) {
            String label = formatTimestamp(chunk.startMs());
            context.append("[").append(idx).append("]");
            if (label != null) {
                context.append(" @ ").append(label);
            }
            context.append("\n").append(chunk.text()).append("\n\n");
            Map<String, Object> cit = new LinkedHashMap<>();
            cit.put("index", idx);
            cit.put("chunkId", chunk.id());
            cit.put("ordinal", chunk.ordinal());
            cit.put("lectureId", chunk.lectureId());
            if (chunk.startMs() != null) {
                cit.put("startMs", chunk.startMs());
                cit.put("timestamp", label);
            }
            cit.put("excerpt", chunk.text().length() > 180 ? chunk.text().substring(0, 180) + "…" : chunk.text());
            citations.add(cit);
            idx++;
        }

        String system = """
                Ты экзаменационный ассистент. Отвечай на русском, опираясь ТОЛЬКО на фрагменты корпуса.
                После ключевых утверждений указывай источники вида [1], [2] или @ mm:ss если есть таймкод.
                Если в корпусе нет ответа — честно скажи об этом.
                """;
        String user = "Вопрос: " + question.trim() + "\n\nФрагменты:\n" + context;
        String answer = llm.complete(system, user);

        String id = UUID.randomUUID().toString();
        String createdAt = Instant.now().toString();
        try {
            jdbc.update(
                    """
                    INSERT INTO qa_turns(id, course_id, question, answer, citations_json, created_at)
                    VALUES (?,?,?,?,?,?)
                    """,
                    id, courseId, question.trim(), answer, objectMapper.writeValueAsString(citations), createdAt);
        } catch (Exception e) {
            throw new IllegalStateException("Не удалось сохранить Q&A: " + e.getMessage(), e);
        }

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("id", id);
        result.put("courseId", courseId);
        result.put("question", question.trim());
        result.put("answer", answer);
        result.put("citations", citations);
        result.put("createdAt", createdAt);
        return result;
    }

    private String formatTimestamp(Long startMs) {
        if (startMs == null) {
            return null;
        }
        long totalSec = startMs / 1000;
        long mm = totalSec / 60;
        long ss = totalSec % 60;
        return String.format("%d:%02d", mm, ss);
    }
}
