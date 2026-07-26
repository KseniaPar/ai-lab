package com.ailab.course;

import com.ailab.conspect.ConspectRepository;
import com.ailab.corpus.ChunkRepository;
import com.ailab.lecture.LectureRepository;
import org.springframework.stereotype.Service;

import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

@Service
public class CourseOutlineService {

    private final CourseService courses;
    private final LectureRepository lectures;
    private final ChunkRepository chunks;
    private final ConspectRepository conspects;

    public CourseOutlineService(
            CourseService courses,
            LectureRepository lectures,
            ChunkRepository chunks,
            ConspectRepository conspects) {
        this.courses = courses;
        this.lectures = lectures;
        this.chunks = chunks;
        this.conspects = conspects;
    }

    public Map<String, Object> outline(String courseId) {
        CourseRepository.CourseRow course = courses.requireOwned(courseId);
        List<LectureRepository.LectureRow> lectureRows = lectures.findByCourse(courseId);

        List<Map<String, Object>> lectureMaps = lectureRows.stream()
                .map(row -> {
                    Map<String, Object> m = new LinkedHashMap<>();
                    m.put("id", row.id());
                    m.put("title", row.title());
                    m.put("sourceType", row.sourceType());
                    m.put("status", row.status());
                    m.put("createdAt", row.createdAt());
                    return m;
                })
                .toList();

        long materialsCount = lectureRows.stream()
                .filter(row -> "MATERIAL".equals(row.sourceType()))
                .count();

        Map<String, Object> courseMap = new LinkedHashMap<>();
        courseMap.put("id", course.id());
        courseMap.put("title", course.title());
        courseMap.put("subject", course.subject() == null ? "" : course.subject());

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("course", courseMap);
        result.put("lectures", lectureMaps);
        result.put("materialsCount", materialsCount);
        result.put("chunksCount", chunks.countByCourse(courseId));
        result.put("hasConspect", conspects.existsByCourse(courseId));
        return result;
    }
}
