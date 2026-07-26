package com.ailab.corpus;

import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public class ChunkRepository {

    public record ChunkRow(
            String id,
            String lectureId,
            String courseId,
            int ordinal,
            String text,
            Long startMs,
            Long endMs) {
    }

    private final JdbcTemplate jdbc;

    public ChunkRepository(JdbcTemplate jdbc) {
        this.jdbc = jdbc;
    }

    public void deleteByCourse(String courseId) {
        jdbc.update("DELETE FROM chunks WHERE course_id = ?", courseId);
    }

    public void insert(ChunkRow row) {
        jdbc.update(
                """
                INSERT INTO chunks(id, lecture_id, course_id, ordinal, text, start_ms, end_ms)
                VALUES (?,?,?,?,?,?,?)
                """,
                row.id(), row.lectureId(), row.courseId(), row.ordinal(), row.text(),
                row.startMs(), row.endMs());
    }

    public List<ChunkRow> findByCourse(String courseId) {
        return jdbc.query(
                """
                SELECT id, lecture_id, course_id, ordinal, text, start_ms, end_ms
                FROM chunks WHERE course_id = ? ORDER BY lecture_id, ordinal
                """,
                (rs, i) -> new ChunkRow(
                        rs.getString("id"),
                        rs.getString("lecture_id"),
                        rs.getString("course_id"),
                        rs.getInt("ordinal"),
                        rs.getString("text"),
                        toLong(rs.getObject("start_ms")),
                        toLong(rs.getObject("end_ms"))),
                courseId);
    }

    public long countByCourse(String courseId) {
        Long n = jdbc.queryForObject(
                "SELECT COUNT(*) FROM chunks WHERE course_id = ?",
                Long.class,
                courseId);
        return n == null ? 0 : n;
    }

    public long countByUser(String userId) {
        Long n = jdbc.queryForObject(
                """
                SELECT COUNT(*) FROM chunks ch
                JOIN courses c ON c.id = ch.course_id
                WHERE c.user_id = ?
                """,
                Long.class,
                userId);
        return n == null ? 0 : n;
    }

    private static Long toLong(Object value) {
        if (value == null) {
            return null;
        }
        if (value instanceof Number number) {
            return number.longValue();
        }
        return Long.parseLong(value.toString());
    }
}
