package com.ailab.qa;

import com.ailab.corpus.CorpusService;
import com.ailab.course.CourseRepository;
import com.ailab.course.CourseService;
import com.ailab.llm.LlmGateway;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.context.SecurityContextHolder;

import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

class AskServiceTest {

    @BeforeEach
    void setUp() {
        SecurityContextHolder.getContext().setAuthentication(
                new UsernamePasswordAuthenticationToken("user-1", null, java.util.List.of()));
    }

    @AfterEach
    void tearDown() {
        SecurityContextHolder.clearContext();
    }

    @Test
    void blankQuestionThrowsRussianErrorContainingQuestion() {
        CourseService courses = mock(CourseService.class);
        when(courses.requireOwned("c1")).thenReturn(
                new CourseRepository.CourseRow("c1", "u1", "Title", "subj", "2026-01-01"));

        AskService service = new AskService(
                courses,
                mock(CorpusService.class),
                mock(LlmGateway.class),
                mock(QaTurnRepository.class),
                mock(AskRateLimiter.class),
                new ObjectMapper());

        IllegalArgumentException ex = assertThrows(
                IllegalArgumentException.class,
                () -> service.ask("c1", "   "));
        assertTrue(ex.getMessage().contains("question"),
                "expected message to contain 'question', got: " + ex.getMessage());
    }
}
