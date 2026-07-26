package com.ailab.course;

import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public class CourseRepository {

    public record CourseRow(String id, String userId, String title, String subject, String createdAt) {
    }

    private final JdbcTemplate jdbc;

    public CourseRepository(JdbcTemplate jdbc) {
        this.jdbc = jdbc;
    }

    public void insert(CourseRow row) {
        jdbc.update(
                "INSERT INTO courses(id, user_id, title, subject, created_at) VALUES (?,?,?,?,?)",
                row.id(), row.userId(), row.title(), row.subject(), row.createdAt());
    }

    public List<CourseRow> findByUser(String userId) {
        return jdbc.query(
                "SELECT id, user_id, title, subject, created_at FROM courses WHERE user_id = ? ORDER BY created_at DESC",
                (rs, i) -> new CourseRow(
                        rs.getString("id"),
                        rs.getString("user_id"),
                        rs.getString("title"),
                        rs.getString("subject"),
                        rs.getString("created_at")),
                userId);
    }

    public Optional<CourseRow> findById(String id) {
        List<CourseRow> rows = jdbc.query(
                "SELECT id, user_id, title, subject, created_at FROM courses WHERE id = ?",
                (rs, i) -> new CourseRow(
                        rs.getString("id"),
                        rs.getString("user_id"),
                        rs.getString("title"),
                        rs.getString("subject"),
                        rs.getString("created_at")),
                id);
        return rows.stream().findFirst();
    }

    public void delete(String id) {
        jdbc.update("DELETE FROM courses WHERE id = ?", id);
    }

    public long countByUser(String userId) {
        Long n = jdbc.queryForObject("SELECT COUNT(*) FROM courses WHERE user_id = ?", Long.class, userId);
        return n == null ? 0 : n;
    }
}
