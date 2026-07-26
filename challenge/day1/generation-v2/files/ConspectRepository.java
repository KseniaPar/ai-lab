package com.ailab.conspect;

import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public class ConspectRepository {

    public record ConspectRow(String id, String courseId, String markdown, String createdAt) {
    }

    private final JdbcTemplate jdbc;

    public ConspectRepository(JdbcTemplate jdbc) {
        this.jdbc = jdbc;
    }

    public void insert(ConspectRow row) {
        jdbc.update(
                "INSERT INTO conspects(id, course_id, markdown, created_at) VALUES (?,?,?,?)",
                row.id(), row.courseId(), row.markdown(), row.createdAt());
    }

    public Optional<ConspectRow> findLatestByCourse(String courseId) {
        List<ConspectRow> rows = jdbc.query(
                """
                SELECT id, course_id, markdown, created_at FROM conspects
                WHERE course_id = ? ORDER BY created_at DESC LIMIT 1
                """,
                (rs, i) -> new ConspectRow(
                        rs.getString("id"),
                        rs.getString("course_id"),
                        rs.getString("markdown"),
                        rs.getString("created_at")),
                courseId);
        return rows.stream().findFirst();
    }

    public boolean existsByCourse(String courseId) {
        List<Integer> rows = jdbc.query(
                "SELECT 1 FROM conspects WHERE course_id = ? LIMIT 1",
                (rs, i) -> 1,
                courseId);
        return !rows.isEmpty();
    }
}
