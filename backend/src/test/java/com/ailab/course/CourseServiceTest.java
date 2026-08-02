package com.ailab.course;

import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.context.SecurityContextHolder;

import java.util.Optional;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

class CourseServiceTest {

    private CourseRepository courses;
    private CourseService service;

    @BeforeEach
    void setUp() {
        courses = mock(CourseRepository.class);
        service = new CourseService(courses);
        SecurityContextHolder.getContext().setAuthentication(
                new UsernamePasswordAuthenticationToken("user-1", null, java.util.List.of()));
    }

    @AfterEach
    void tearDown() {
        SecurityContextHolder.clearContext();
    }

    @Test
    void requireOwnedThrowsWhenCourseMissing() {
        when(courses.findById("missing")).thenReturn(Optional.empty());

        IllegalArgumentException ex = assertThrows(
                IllegalArgumentException.class,
                () -> service.requireOwned("missing"));
        assertEquals("Курс не найден", ex.getMessage());
    }

    @Test
    void requireOwnedThrowsSecurityExceptionForWrongOwner() {
        when(courses.findById("c1")).thenReturn(Optional.of(
                new CourseRepository.CourseRow("c1", "other-user", "Title", "subj", "2026-01-01")));

        SecurityException ex = assertThrows(
                SecurityException.class,
                () -> service.requireOwned("c1"));
        assertEquals("Нет доступа к курсу", ex.getMessage());
    }
}
