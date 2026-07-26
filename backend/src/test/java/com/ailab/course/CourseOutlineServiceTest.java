package com.ailab.course;

import com.ailab.conspect.ConspectRepository;
import com.ailab.corpus.ChunkRepository;
import com.ailab.lecture.LectureRepository;
import org.junit.jupiter.api.Test;

import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

class CourseOutlineServiceTest {

    @Test
    void outlineCountsMaterialsAndNullSubject() {
        CourseService courses = mock(CourseService.class);
        LectureRepository lectures = mock(LectureRepository.class);
        ChunkRepository chunks = mock(ChunkRepository.class);
        ConspectRepository conspects = mock(ConspectRepository.class);

        CourseRepository.CourseRow course = new CourseRepository.CourseRow(
                "c1", "u1", "Алгебра", null, "2026-01-01");
        when(courses.requireOwned("c1")).thenReturn(course);
        when(lectures.findByCourse("c1")).thenReturn(List.of(
                lecture("l1", "AUDIO", "READY"),
                lecture("l2", "MATERIAL", "READY"),
                lecture("l3", "MATERIAL", "READY")));
        when(chunks.countByCourse("c1")).thenReturn(12L);
        when(conspects.existsByCourse("c1")).thenReturn(true);

        CourseOutlineService service = new CourseOutlineService(courses, lectures, chunks, conspects);
        Map<String, Object> outline = service.outline("c1");

        @SuppressWarnings("unchecked")
        Map<String, Object> courseMap = (Map<String, Object>) outline.get("course");
        assertEquals("c1", courseMap.get("id"));
        assertEquals("Алгебра", courseMap.get("title"));
        assertEquals("", courseMap.get("subject"));

        @SuppressWarnings("unchecked")
        List<Map<String, Object>> lectureMaps = (List<Map<String, Object>>) outline.get("lectures");
        assertEquals(3, lectureMaps.size());
        assertEquals(2L, outline.get("materialsCount"));
        assertEquals(12L, outline.get("chunksCount"));
        assertTrue((Boolean) outline.get("hasConspect"));
    }

    @Test
    void outlineEmptyCourse() {
        CourseService courses = mock(CourseService.class);
        LectureRepository lectures = mock(LectureRepository.class);
        ChunkRepository chunks = mock(ChunkRepository.class);
        ConspectRepository conspects = mock(ConspectRepository.class);

        when(courses.requireOwned("c2")).thenReturn(
                new CourseRepository.CourseRow("c2", "u1", "Пустой", "math", "2026-01-02"));
        when(lectures.findByCourse("c2")).thenReturn(List.of());
        when(chunks.countByCourse("c2")).thenReturn(0L);
        when(conspects.existsByCourse("c2")).thenReturn(false);

        CourseOutlineService service = new CourseOutlineService(courses, lectures, chunks, conspects);
        Map<String, Object> outline = service.outline("c2");

        assertEquals(0L, outline.get("materialsCount"));
        assertEquals(0L, outline.get("chunksCount"));
        assertFalse((Boolean) outline.get("hasConspect"));
        assertEquals(List.of(), outline.get("lectures"));
    }

    private static LectureRepository.LectureRow lecture(String id, String sourceType, String status) {
        return new LectureRepository.LectureRow(
                id, "c1", "L-" + id, sourceType, status, null, null, "2026-01-01");
    }
}
