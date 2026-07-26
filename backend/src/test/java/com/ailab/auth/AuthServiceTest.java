package com.ailab.auth;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.security.crypto.password.PasswordEncoder;

import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

class AuthServiceTest {

    private InMemoryUsers users;
    private AuthService auth;

    @BeforeEach
    void setUp() {
        users = new InMemoryUsers();
        PasswordEncoder encoder = new PasswordEncoder() {
            @Override
            public String encode(CharSequence rawPassword) {
                return "enc:" + rawPassword;
            }

            @Override
            public boolean matches(CharSequence rawPassword, String encodedPassword) {
                return encodedPassword.equals("enc:" + rawPassword);
            }
        };
        JwtService jwt = new JwtService("auth-service-test-secret-32b!!!!!", 3_600_000L);
        auth = new AuthService(users, encoder, jwt);
    }

    @Test
    void registerRejectsBlankUsername() {
        IllegalArgumentException ex = assertThrows(
                IllegalArgumentException.class,
                () -> auth.register("  ", "password"));
        assertTrue(ex.getMessage().contains("username"));
    }

    @Test
    void registerRejectsShortPassword() {
        assertThrows(IllegalArgumentException.class, () -> auth.register("alice", "abc"));
    }

    @Test
    void registerCreatesUserAndReturnsToken() {
        Map<String, Object> result = auth.register(" alice ", "secret");
        assertEquals("alice", result.get("username"));
        assertTrue(result.get("token") instanceof String);
        assertTrue(users.findByUsername("alice").isPresent());
    }

    @Test
    void registerRejectsDuplicateUsername() {
        auth.register("alice", "secret");
        assertThrows(IllegalStateException.class, () -> auth.register("alice", "other"));
    }

    @Test
    void loginSucceedsWithMatchingPassword() {
        Map<String, Object> registered = auth.register("bob", "pass");
        Map<String, Object> loggedIn = auth.login(" bob ", "pass");
        assertEquals(registered.get("userId"), loggedIn.get("userId"));
        assertEquals("bob", loggedIn.get("username"));
    }

    @Test
    void loginRejectsWrongPassword() {
        auth.register("bob", "pass");
        assertThrows(IllegalArgumentException.class, () -> auth.login("bob", "wrong"));
    }

    @Test
    void loginRejectsUnknownUser() {
        assertThrows(IllegalArgumentException.class, () -> auth.login("nobody", "pass"));
    }

    /**
     * Minimal fake — AuthService only needs findByUsername + insert.
     */
    private static final class InMemoryUsers extends UserRepository {
        private final Map<String, UserRow> byUsername = new HashMap<>();

        InMemoryUsers() {
            super(null);
        }

        @Override
        public void insert(String id, String username, String passwordHash, String createdAt) {
            byUsername.put(username, new UserRow(id, username, passwordHash));
        }

        @Override
        public Optional<UserRow> findByUsername(String username) {
            return Optional.ofNullable(byUsername.get(username));
        }
    }
}
