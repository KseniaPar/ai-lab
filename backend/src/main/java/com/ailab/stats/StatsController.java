package com.ailab.stats;

import com.ailab.auth.AuthContext;
import com.ailab.corpus.ChunkRepository;
import com.ailab.course.CourseRepository;
import com.ailab.lecture.LectureRepository;
import com.ailab.stt.TranscriptionClient;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.LinkedHashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/stats")
public class StatsController {

    private final CourseRepository courses;
    private final LectureRepository lectures;
    private final ChunkRepository chunks;
    private final JdbcTemplate jdbc;
    private final TranscriptionClient transcriptionClient;

    public StatsController(
            CourseRepository courses,
            LectureRepository lectures,
            ChunkRepository chunks,
            JdbcTemplate jdbc,
            TranscriptionClient transcriptionClient) {
        this.courses = courses;
        this.lectures = lectures;
        this.chunks = chunks;
        this.jdbc = jdbc;
        this.transcriptionClient = transcriptionClient;
    }

    @GetMapping
    public Map<String, Object> stats() {
        String userId = AuthContext.requireUserId();
        String lastAsk = null;
        try {
            lastAsk = jdbc.query(
                    """
                    SELECT q.created_at FROM qa_turns q
                    JOIN courses c ON c.id = q.course_id
                    WHERE c.user_id = ?
                    ORDER BY q.created_at DESC LIMIT 1
                    """,
                    rs -> rs.next() ? rs.getString(1) : null,
                    userId);
        } catch (Exception ignored) {
            // empty
        }
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("courseCount", courses.countByUser(userId));
        result.put("lectureCount", lectures.countByUserCourses(userId));
        result.put("chunkCount", chunks.countByUser(userId));
        result.put("lastAskAt", lastAsk == null ? "" : lastAsk);
        result.put("stt", transcriptionClient.status());
        return result;
    }
}
