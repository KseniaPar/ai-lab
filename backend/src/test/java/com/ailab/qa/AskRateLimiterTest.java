package com.ailab.qa;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertThrows;

class AskRateLimiterTest {

    @Test
    void allowsUpToLimitThenThrows() {
        AskRateLimiter limiter = new AskRateLimiter(2);
        assertDoesNotThrow(() -> limiter.check("u1"));
        assertDoesNotThrow(() -> limiter.check("u1"));
        assertThrows(IllegalStateException.class, () -> limiter.check("u1"));
    }

    @Test
    void limitsArePerUser() {
        AskRateLimiter limiter = new AskRateLimiter(1);
        assertDoesNotThrow(() -> limiter.check("u1"));
        assertDoesNotThrow(() -> limiter.check("u2"));
        assertThrows(IllegalStateException.class, () -> limiter.check("u1"));
    }
}
