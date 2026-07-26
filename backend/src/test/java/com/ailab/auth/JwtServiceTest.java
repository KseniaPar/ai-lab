package com.ailab.auth;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.JwtException;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

class JwtServiceTest {

    @Test
    void createAndParseRoundTrip() {
        JwtService jwt = new JwtService("unit-test-secret-at-least-32-bytes!!", 3_600_000L);
        String token = jwt.createToken("user-1", "alice");
        Claims claims = jwt.parse(token);
        assertEquals("user-1", claims.getSubject());
        assertEquals("alice", claims.get("username", String.class));
    }

    @Test
    void shortSecretIsPaddedAndUsable() {
        JwtService jwt = new JwtService("short", 60_000L);
        String token = jwt.createToken("id", "bob");
        assertEquals("id", jwt.parse(token).getSubject());
    }

    @Test
    void rejectTamperedToken() {
        JwtService jwt = new JwtService("unit-test-secret-at-least-32-bytes!!", 3_600_000L);
        String token = jwt.createToken("user-1", "alice");
        String tampered = token.substring(0, token.length() - 4) + "xxxx";
        assertThrows(JwtException.class, () -> jwt.parse(tampered));
    }

    @Test
    void rejectTokenSignedWithDifferentSecret() {
        JwtService issuer = new JwtService("unit-test-secret-at-least-32-bytes!!", 3_600_000L);
        JwtService other = new JwtService("another-secret-at-least-32-bytes!!xx", 3_600_000L);
        String token = issuer.createToken("user-1", "alice");
        assertThrows(JwtException.class, () -> other.parse(token));
    }

    @Test
    void tokenIsCompactJwt() {
        JwtService jwt = new JwtService("unit-test-secret-at-least-32-bytes!!", 3_600_000L);
        String token = jwt.createToken("u", "n");
        assertTrue(token.chars().filter(c -> c == '.').count() == 2);
    }
}
