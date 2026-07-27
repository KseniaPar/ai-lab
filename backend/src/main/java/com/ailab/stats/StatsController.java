package com.ailab.stats;

import com.ailab.auth.AuthContext;
import com.ailab.conspect.ConspectRepository;
import com.ailab.corpus.ChunkRepository;
import com.ailab.course.CourseRepository;
import com.ailab.lecture.LectureRepository;
import com.ailab.qa.QaTurnRepository;
import com.ailab.stt.TranscriptionClient;
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
    private final ConspectRepository conspects;
    private final QaTurnRepository qaTurns;
    private final TranscriptionClient transcriptionClient;

    public StatsController(
            CourseRepository courses,
            LectureRepository lectures,
            ChunkRepository chunks,
            ConspectRepository conspects,
            QaTurnRepository qaTurns,
            TranscriptionClient transcriptionClient) {
        this.courses = courses;
        this.lectures = lectures;
        this.chunks = chunks;
        this.conspects = conspects;
        this.qaTurns = qaTurns;
        this.transcriptionClient = transcriptionClient;
    }

    @GetMapping
    public Map<String, Object> stats() {
        String userId = AuthContext.requireUserId();
        String lastAsk = null;
        try {
            lastAsk = qaTurns.findLatestCreatedAtByUser(userId);
        } catch (Exception ignored) {
            // empty
        }
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("courseCount", courses.countByUser(userId));
        result.put("lectureCount", lectures.countByUserCourses(userId));
        result.put("chunkCount", chunks.countByUser(userId));
        result.put("hasAnyConspect", conspects.existsByUser(userId));
        result.put("lastAskAt", lastAsk == null ? "" : lastAsk);
        result.put("stt", transcriptionClient.status());
        return result;
    }
}
