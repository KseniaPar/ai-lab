package com.ailab.qa;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import java.util.ArrayDeque;
import java.util.Deque;
import java.util.concurrent.ConcurrentHashMap;

@Component
public class AskRateLimiter {

    private final int limitPerMinute;
    private final ConcurrentHashMap<String, Deque<Long>> hitsByUser = new ConcurrentHashMap<>();

    public AskRateLimiter(@Value("${app.ask.rate-limit-per-minute:30}") int limitPerMinute) {
        this.limitPerMinute = limitPerMinute;
    }

    public void check(String userId) {
        long now = System.currentTimeMillis();
        long windowStart = now - 60_000L;
        Deque<Long> hits = hitsByUser.computeIfAbsent(userId, id -> new ArrayDeque<>());
        synchronized (hits) {
            while (!hits.isEmpty() && hits.peekFirst() < windowStart) {
                hits.removeFirst();
            }
            if (hits.size() >= limitPerMinute) {
                throw new IllegalStateException("Превышен лимит вопросов — подождите минуту");
            }
            hits.addLast(now);
        }
    }
}
