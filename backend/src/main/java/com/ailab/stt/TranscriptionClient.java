package com.ailab.stt;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.stereotype.Component;
import org.springframework.web.client.HttpStatusCodeException;
import org.springframework.web.client.RestTemplate;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Base64;
import java.util.List;
import java.util.Locale;
import java.util.Map;

@Component
public class TranscriptionClient {

    private static final Logger log = LoggerFactory.getLogger(TranscriptionClient.class);

    public record Segment(long startMs, long endMs, String text) {
    }

    public record Result(String text, List<Segment> segments) {
    }

    private final RestTemplate restTemplate;
    private final ObjectMapper objectMapper;
    private final String apiKey;
    private final String url;
    private final String model;
    private final String fallbackModel;

    public TranscriptionClient(
            ObjectMapper objectMapper,
            @Value("${app.openrouter.api-key:}") String apiKey,
            @Value("${app.openrouter.base-url}") String baseUrl,
            @Value("${app.stt.model}") String model,
            @Value("${app.stt.fallback-model}") String fallbackModel) {
        this.objectMapper = objectMapper;
        this.apiKey = apiKey == null ? "" : apiKey.trim();
        this.url = baseUrl + "/v1/audio/transcriptions";
        this.model = model;
        this.fallbackModel = fallbackModel;
        SimpleClientHttpRequestFactory factory = new SimpleClientHttpRequestFactory();
        factory.setConnectTimeout(30_000);
        factory.setReadTimeout(180_000);
        this.restTemplate = new RestTemplate(factory);
        if (configured()) {
            log.info("STT configured: keyPrefix={}… len={} url={}",
                    this.apiKey.substring(0, Math.min(10, this.apiKey.length())),
                    this.apiKey.length(),
                    this.url);
        } else {
            log.warn("STT NOT configured — check application-local.yml app.openrouter.api-key");
        }
    }

    public boolean configured() {
        return apiKey.startsWith("sk-or-") && apiKey.length() > 20;
    }

    public Map<String, Object> status() {
        return Map.of(
                "configured", configured(),
                "keyPrefix", configured() ? apiKey.substring(0, Math.min(12, apiKey.length())) + "…" : "",
                "keyLength", apiKey.length(),
                "url", url,
                "model", model);
    }

    public Result transcribe(Path audioPath) {
        if (!configured()) {
            throw new IllegalStateException(
                    "OPENROUTER_API_KEY не задан или неверный формат (ожидается sk-or-…). "
                            + "Проверь application-local.yml и перезапуск backend.");
        }
        if (audioPath == null || !Files.isRegularFile(audioPath)) {
            throw new IllegalArgumentException("Аудиофайл не найден");
        }
        try {
            byte[] bytes = Files.readAllBytes(audioPath);
            long size = bytes.length;
            String useModel = size > 25L * 1024 * 1024 ? fallbackModel : model;
            String format = detectFormat(audioPath.getFileName().toString());
            String b64 = Base64.getEncoder().encodeToString(bytes);

            ObjectNode rootReq = objectMapper.createObjectNode();
            rootReq.put("model", useModel);
            rootReq.put("language", "ru");
            rootReq.put("response_format", "verbose_json");
            ObjectNode inputAudio = rootReq.putObject("input_audio");
            inputAudio.put("data", b64);
            inputAudio.put("format", format);

            HttpHeaders headers = new HttpHeaders();
            headers.setBearerAuth(apiKey);
            headers.setContentType(MediaType.APPLICATION_JSON);
            headers.add("HTTP-Referer", "https://github.com/ailab/knowbase");
            headers.add("X-Title", "Knowbase");

            log.info("OpenRouter STT POST {} model={} format={} size={}KB",
                    url, useModel, format, size / 1024);

            ResponseEntity<String> response = restTemplate.postForEntity(
                    url, new HttpEntity<>(objectMapper.writeValueAsString(rootReq), headers), String.class);
            return parseResponse(response.getBody());
        } catch (HttpStatusCodeException e) {
            String body = e.getResponseBodyAsString();
            log.error("STT HTTP {}: {}", e.getStatusCode().value(), body);
            if (e.getStatusCode().value() == 401) {
                throw new IllegalStateException(
                        "STT 401 Unauthorized — ключ OpenRouter отклонён. "
                                + "Проверь ключ на https://openrouter.ai/keys "
                                + "(должен начинаться с sk-or-v1-), кредиты на счёте, "
                                + "и что в application-local.yml нет кавычек/пробелов. "
                                + "После правки перезапусти backend. body=" + body,
                        e);
            }
            throw new IllegalStateException("STT failed HTTP " + e.getStatusCode().value() + ": " + body, e);
        } catch (IllegalStateException e) {
            throw e;
        } catch (Exception e) {
            throw new IllegalStateException("STT failed: " + e.getMessage(), e);
        }
    }

    private Result parseResponse(String body) throws Exception {
        JsonNode root = objectMapper.readTree(body);
        String text = root.path("text").asText("");
        List<Segment> segments = new ArrayList<>();
        if (root.has("segments") && root.get("segments").isArray()) {
            for (JsonNode seg : root.get("segments")) {
                double start = seg.path("start").asDouble(0);
                double end = seg.path("end").asDouble(start);
                String segText = seg.path("text").asText("").trim();
                if (!segText.isBlank()) {
                    segments.add(new Segment(Math.round(start * 1000), Math.round(end * 1000), segText));
                }
            }
        }
        if (text.isBlank() && !segments.isEmpty()) {
            text = segments.stream().map(Segment::text).reduce((a, b) -> a + " " + b).orElse("");
        }
        return new Result(text.trim(), segments);
    }

    private String detectFormat(String filename) {
        String lower = filename.toLowerCase(Locale.ROOT);
        if (lower.endsWith(".mp3")) return "mp3";
        if (lower.endsWith(".wav")) return "wav";
        if (lower.endsWith(".m4a")) return "m4a";
        if (lower.endsWith(".ogg")) return "ogg";
        if (lower.endsWith(".flac")) return "flac";
        if (lower.endsWith(".webm")) return "webm";
        if (lower.endsWith(".aac")) return "aac";
        if (lower.endsWith(".mp4")) return "mp4";
        return "mp3";
    }
}
