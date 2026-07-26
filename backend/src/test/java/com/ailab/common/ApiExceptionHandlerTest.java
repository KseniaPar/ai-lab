package com.ailab.common;

import org.junit.jupiter.api.Test;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;

import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;

class ApiExceptionHandlerTest {

    private final ApiExceptionHandler handler = new ApiExceptionHandler();

    @Test
    void illegalArgumentIsBadRequest() {
        ResponseEntity<Map<String, String>> res =
                handler.badRequest(new IllegalArgumentException("title обязателен"));
        assertEquals(HttpStatus.BAD_REQUEST, res.getStatusCode());
        assertEquals("title обязателен", res.getBody().get("error"));
    }

    @Test
    void illegalStateIsConflict() {
        ResponseEntity<Map<String, String>> res =
                handler.conflict(new IllegalStateException("Пользователь уже существует"));
        assertEquals(HttpStatus.CONFLICT, res.getStatusCode());
        assertEquals("Пользователь уже существует", res.getBody().get("error"));
    }

    @Test
    void securityExceptionIsForbidden() {
        ResponseEntity<Map<String, String>> res =
                handler.forbidden(new SecurityException("Нет доступа к курсу"));
        assertEquals(HttpStatus.FORBIDDEN, res.getStatusCode());
        assertEquals("Нет доступа к курсу", res.getBody().get("error"));
    }

    @Test
    void otherExceptionIsInternalServerError() {
        ResponseEntity<Map<String, String>> res =
                handler.other(new RuntimeException("boom"));
        assertEquals(HttpStatus.INTERNAL_SERVER_ERROR, res.getStatusCode());
        assertEquals("boom", res.getBody().get("error"));
    }

    @Test
    void nullMessageFallsBackToClassName() {
        ResponseEntity<Map<String, String>> res =
                handler.other(new RuntimeException((String) null));
        assertEquals(HttpStatus.INTERNAL_SERVER_ERROR, res.getStatusCode());
        assertEquals("RuntimeException", res.getBody().get("error"));
    }
}
