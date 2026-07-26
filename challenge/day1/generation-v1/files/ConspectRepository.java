package com.ailab.conspect;

import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;

@Repository
public class ConspectRepository {

    private final JdbcTemplate jdbc;

    public ConspectRepository(JdbcTemplate jdbc) {
        this.jdbc = jdbc;
    }

    public boolean existsByCourse(String courseId) {
        Long n = jdbc.queryForObject(
                "SELECT COUNT(*) FROM conspects WHERE course_id = ?",
                Long.class,
                courseId);
        return n != null && n > 0;
    }
}
