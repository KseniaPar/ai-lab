package com.ailab.qa;

import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;

@Repository
public class QaTurnRepository {

    public record QaTurnRow(
            String id,
            String courseId,
            String question,
            String answer,
            String citationsJson,
            String createdAt) {
    }

    private final JdbcTemplate jdbc;

    public QaTurnRepository(JdbcTemplate jdbc) {
        this.jdbc = jdbc;
    }

    public void insert(QaTurnRow row) {
        jdbc.update(
                """
                INSERT INTO qa_turns(id, course_id, question, answer, citations_json, created_at)
                VALUES (?,?,?,?,?,?)
                """,
                row.id(), row.courseId(), row.question(), row.answer(),
                row.citationsJson(), row.createdAt());
    }

    public String findLatestCreatedAtByUser(String userId) {
        return jdbc.query(
                """
                SELECT q.created_at FROM qa_turns q
                JOIN courses c ON c.id = q.course_id
                WHERE c.user_id = ?
                ORDER BY q.created_at DESC LIMIT 1
                """,
                rs -> rs.next() ? rs.getString(1) : null,
                userId);
    }
}
