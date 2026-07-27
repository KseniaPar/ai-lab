package com.ailab.course;

import com.ailab.lecture.LectureRepository;
import org.springframework.stereotype.Service;

import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

@Service
public class CourseSourceSummaryService {

    private final CourseService courses;
    private final LectureRepository lectures;

    public CourseSourceSummaryService(CourseService courses, LectureRepository lectures) {
        this.courses = courses;
        this.lectures = lectures;
    }

    public Map<String, Object> sourceSummary(String courseId) {
        CourseRepository.CourseRow course = courses.requireOwned(courseId);
        List<LectureRepository.LectureRow> rows = lectures.findByCourse(courseId);

        List<Map<String, Object>> sources = rows.stream()
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

        long audioCount = rows.stream().filter(r -> "AUDIO".equals(r.sourceType())).count();
        long materialCount = rows.stream().filter(r -> "MATERIAL".equals(r.sourceType())).count();
        long readyCount = rows.stream().filter(r -> "READY".equals(r.status())).count();

        Map<String, Object> courseMap = new LinkedHashMap<>();
        courseMap.put("id", course.id());
        courseMap.put("title", course.title());
        courseMap.put("subject", course.subject() == null ? "" : course.subject());

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("course", courseMap);
        result.put("sources", sources);
        result.put("audioCount", audioCount);
        result.put("materialCount", materialCount);
        result.put("readyCount", readyCount);
        return result;
    }
}
