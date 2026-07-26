package com.ailab.qa;

import org.junit.jupiter.api.Test;

import java.lang.reflect.Method;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;

/**
 * Citations in the UI show {@code @ mm:ss}. Seconds must be zero-padded
 * so 65000ms → {@code 1:05}, not {@code 1:5}.
 */
class CitationTimestampTest {

    @Test
    void formatsZeroPaddedSeconds() throws Exception {
        AskService ask = new AskService(null, null, null, null, null);
        Method m = AskService.class.getDeclaredMethod("formatTimestamp", Long.class);
        m.setAccessible(true);
        assertEquals("1:05", m.invoke(ask, 65_000L));
        assertEquals("0:05", m.invoke(ask, 5_000L));
        assertEquals("12:00", m.invoke(ask, 720_000L));
        assertNull(m.invoke(ask, new Object[]{null}));
    }
}
