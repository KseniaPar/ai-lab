package com.ailab.auth;

import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.time.Instant;
import java.util.Map;
import java.util.UUID;

@Service
public class AuthService {

    private final UserRepository users;
    private final PasswordEncoder passwordEncoder;
    private final JwtService jwtService;

    public AuthService(UserRepository users, PasswordEncoder passwordEncoder, JwtService jwtService) {
        this.users = users;
        this.passwordEncoder = passwordEncoder;
        this.jwtService = jwtService;
    }

    public Map<String, Object> register(String username, String password) {
        if (username == null || username.isBlank() || password == null || password.length() < 4) {
            throw new IllegalArgumentException("username обязателен, password минимум 4 символа");
        }
        String normalized = username.trim();
        if (users.findByUsername(normalized).isPresent()) {
            throw new IllegalStateException("Пользователь уже существует");
        }
        String id = UUID.randomUUID().toString();
        users.insert(id, normalized, passwordEncoder.encode(password), Instant.now().toString());
        String token = jwtService.createToken(id, normalized);
        return Map.of("token", token, "userId", id, "username", normalized);
    }

    public Map<String, Object> login(String username, String password) {
        UserRepository.UserRow user = users.findByUsername(username == null ? "" : username.trim())
                .orElseThrow(() -> new IllegalArgumentException("Неверный логин или пароль"));
        if (!passwordEncoder.matches(password, user.passwordHash())) {
            throw new IllegalArgumentException("Неверный логин или пароль");
        }
        String token = jwtService.createToken(user.id(), user.username());
        return Map.of("token", token, "userId", user.id(), "username", user.username());
    }
}
