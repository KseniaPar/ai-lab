package com.ailab.lecture;

import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public class LectureRepository {

    public record LectureRow(
            String id,
            String courseId,
            String title,
            String sourceType,
            String status,
            String rawText,
            String audioPath,
            String createdAt) {
    }

    public record SegmentRow(String id, String lectureId, long startMs, long endMs, String text, int ordinal) {
    }

    private final JdbcTemplate jdbc;

    public LectureRepository(JdbcTemplate jdbc) {
        this.jdbc = jdbc;
    }

    public void insert(LectureRow row) {
        jdbc.update(
                """
                INSERT INTO lectures(id, course_id, title, source_type, status, raw_text, audio_path, created_at)
                VALUES (?,?,?,?,?,?,?,?)
                """,
                row.id(), row.courseId(), row.title(), row.sourceType(), row.status(),
                row.rawText(), row.audioPath(), row.createdAt());
    }

    public void updateStatusAndText(String id, String status, String rawText) {
        jdbc.update("UPDATE lectures SET status = ?, raw_text = ? WHERE id = ?", status, rawText, id);
    }

    public Optional<LectureRow> findById(String id) {
        List<LectureRow> rows = jdbc.query(
                """
                SELECT id, course_id, title, source_type, status, raw_text, audio_path, created_at
                FROM lectures WHERE id = ?
                """,
                (rs, i) -> new LectureRow(
                        rs.getString("id"),
                        rs.getString("course_id"),
                        rs.getString("title"),
                        rs.getString("source_type"),
                        rs.getString("status"),
                        rs.getString("raw_text"),
                        rs.getString("audio_path"),
                        rs.getString("created_at")),
                id);
        return rows.stream().findFirst();
    }

    public List<LectureRow> findByCourse(String courseId) {
        return jdbc.query(
                """
                SELECT id, course_id, title, source_type, status, raw_text, audio_path, created_at
                FROM lectures WHERE course_id = ? ORDER BY created_at
                """,
                (rs, i) -> new LectureRow(
                        rs.getString("id"),
                        rs.getString("course_id"),
                        rs.getString("title"),
                        rs.getString("source_type"),
                        rs.getString("status"),
                        rs.getString("raw_text"),
                        rs.getString("audio_path"),
                        rs.getString("created_at")),
                courseId);
    }

    public void insertSegment(SegmentRow row) {
        jdbc.update(
                """
                INSERT INTO transcript_segments(id, lecture_id, start_ms, end_ms, text, ordinal)
                VALUES (?,?,?,?,?,?)
                """,
                row.id(), row.lectureId(), row.startMs(), row.endMs(), row.text(), row.ordinal());
    }

    public void deleteSegments(String lectureId) {
        jdbc.update("DELETE FROM transcript_segments WHERE lecture_id = ?", lectureId);
    }

    public List<SegmentRow> findSegments(String lectureId) {
        return jdbc.query(
                """
                SELECT id, lecture_id, start_ms, end_ms, text, ordinal
                FROM transcript_segments WHERE lecture_id = ? ORDER BY ordinal
                """,
                (rs, i) -> new SegmentRow(
                        rs.getString("id"),
                        rs.getString("lecture_id"),
                        rs.getLong("start_ms"),
                        rs.getLong("end_ms"),
                        rs.getString("text"),
                        rs.getInt("ordinal")),
                lectureId);
    }

    public long countByCourseAndSourceType(String courseId, String sourceType) {
        Long n = jdbc.queryForObject(
                "SELECT COUNT(*) FROM lectures WHERE course_id = ? AND source_type = ?",
                Long.class,
                courseId,
                sourceType);
        return n == null ? 0 : n;
    }

    public long countByUserCourses(String userId) {
        Long n = jdbc.queryForObject(
                """
                SELECT COUNT(*) FROM lectures l
                JOIN courses c ON c.id = l.course_id
                WHERE c.user_id = ?
                """,
                Long.class,
                userId);
        return n == null ? 0 : n;
    }
}
