package com.ailab.db;

import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Component;

import jakarta.annotation.PostConstruct;

@Component
public class SchemaInitializer {

    private final JdbcTemplate jdbc;

    public SchemaInitializer(JdbcTemplate jdbc) {
        this.jdbc = jdbc;
    }

    @PostConstruct
    public void init() {
        jdbc.execute("""
                CREATE TABLE IF NOT EXISTS users (
                  id TEXT PRIMARY KEY,
                  username TEXT NOT NULL UNIQUE,
                  password_hash TEXT NOT NULL,
                  created_at TEXT NOT NULL
                )
                """);
        jdbc.execute("""
                CREATE TABLE IF NOT EXISTS courses (
                  id TEXT PRIMARY KEY,
                  user_id TEXT NOT NULL,
                  title TEXT NOT NULL,
                  subject TEXT,
                  created_at TEXT NOT NULL,
                  FOREIGN KEY(user_id) REFERENCES users(id)
                )
                """);
        jdbc.execute("""
                CREATE TABLE IF NOT EXISTS lectures (
                  id TEXT PRIMARY KEY,
                  course_id TEXT NOT NULL,
                  title TEXT NOT NULL,
                  source_type TEXT NOT NULL,
                  status TEXT NOT NULL,
                  raw_text TEXT,
                  audio_path TEXT,
                  created_at TEXT NOT NULL,
                  FOREIGN KEY(course_id) REFERENCES courses(id)
                )
                """);
        jdbc.execute("""
                CREATE TABLE IF NOT EXISTS transcript_segments (
                  id TEXT PRIMARY KEY,
                  lecture_id TEXT NOT NULL,
                  start_ms INTEGER NOT NULL,
                  end_ms INTEGER NOT NULL,
                  text TEXT NOT NULL,
                  ordinal INTEGER NOT NULL,
                  FOREIGN KEY(lecture_id) REFERENCES lectures(id)
                )
                """);
        jdbc.execute("""
                CREATE TABLE IF NOT EXISTS chunks (
                  id TEXT PRIMARY KEY,
                  lecture_id TEXT NOT NULL,
                  course_id TEXT NOT NULL,
                  ordinal INTEGER NOT NULL,
                  text TEXT NOT NULL,
                  start_ms INTEGER,
                  end_ms INTEGER,
                  FOREIGN KEY(lecture_id) REFERENCES lectures(id),
                  FOREIGN KEY(course_id) REFERENCES courses(id)
                )
                """);
        jdbc.execute("""
                CREATE TABLE IF NOT EXISTS conspects (
                  id TEXT PRIMARY KEY,
                  course_id TEXT NOT NULL,
                  markdown TEXT NOT NULL,
                  created_at TEXT NOT NULL,
                  FOREIGN KEY(course_id) REFERENCES courses(id)
                )
                """);
        jdbc.execute("""
                CREATE TABLE IF NOT EXISTS qa_turns (
                  id TEXT PRIMARY KEY,
                  course_id TEXT NOT NULL,
                  question TEXT NOT NULL,
                  answer TEXT NOT NULL,
                  citations_json TEXT NOT NULL,
                  created_at TEXT NOT NULL,
                  FOREIGN KEY(course_id) REFERENCES courses(id)
                )
                """);
    }
}
