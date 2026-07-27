package com.ailab.qa;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

class AskRateLimiterTest {

    @Test
    void allowsUpToLimitThenThrows() {
        AskRateLimiter limiter = new AskRateLimiter(2);
        assertDoesNotThrow(() -> limiter.check("u1"));
        assertDoesNotThrow(() -> limiter.check("u1"));
        IllegalStateException ex = assertThrows(IllegalStateException.class, () -> limiter.check("u1"));
        assertTrue(ex.getMessage().contains("лимит"), "expected Russian rate-limit message");
        assertEquals("Превышен лимит вопросов — подождите минуту", ex.getMessage());
    }

    @Test
    void limitsArePerUser() {
        AskRateLimiter limiter = new AskRateLimiter(1);
        assertDoesNotThrow(() -> limiter.check("u1"));
        assertDoesNotThrow(() -> limiter.check("u2"));
        IllegalStateException ex = assertThrows(IllegalStateException.class, () -> limiter.check("u1"));
        assertTrue(ex.getMessage().contains("лимит"));
    }

    @Test
    void nthPlusOneInWindowThrowsRussianMessage() {
        int n = 3;
        AskRateLimiter limiter = new AskRateLimiter(n);
        for (int i = 0; i < n; i++) {
            assertDoesNotThrow(() -> limiter.check("window-user"));
        }
        IllegalStateException ex = assertThrows(IllegalStateException.class,
                () -> limiter.check("window-user"));
        assertEquals("Превышен лимит вопросов — подождите минуту", ex.getMessage());
    }
}
