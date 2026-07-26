package com.ailab.auth;

import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public class UserRepository {

    public record UserRow(String id, String username, String passwordHash) {
    }

    private final JdbcTemplate jdbc;

    public UserRepository(JdbcTemplate jdbc) {
        this.jdbc = jdbc;
    }

    public void insert(String id, String username, String passwordHash, String createdAt) {
        jdbc.update(
                "INSERT INTO users(id, username, password_hash, created_at) VALUES (?,?,?,?)",
                id, username, passwordHash, createdAt);
    }

    public Optional<UserRow> findByUsername(String username) {
        List<UserRow> rows = jdbc.query(
                "SELECT id, username, password_hash FROM users WHERE username = ?",
                (rs, i) -> new UserRow(rs.getString("id"), rs.getString("username"), rs.getString("password_hash")),
                username);
        return rows.stream().findFirst();
    }

    public Optional<UserRow> findById(String id) {
        List<UserRow> rows = jdbc.query(
                "SELECT id, username, password_hash FROM users WHERE id = ?",
                (rs, i) -> new UserRow(rs.getString("id"), rs.getString("username"), rs.getString("password_hash")),
                id);
        return rows.stream().findFirst();
    }
}
