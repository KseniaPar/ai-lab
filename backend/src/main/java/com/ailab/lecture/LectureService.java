package com.ailab.lecture;

import com.ailab.corpus.CorpusService;
import com.ailab.course.CourseService;
import com.ailab.stt.TranscriptionClient;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Instant;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.UUID;

@Service
public class LectureService {

    private final LectureRepository lectures;
    private final CourseService courses;
    private final TranscriptionClient transcriptionClient;
    private final CorpusService corpusService;
    private final TranscriptionJobService transcriptionJobService;
    private final Path uploadsDir;

    public LectureService(
            LectureRepository lectures,
            CourseService courses,
            TranscriptionClient transcriptionClient,
            CorpusService corpusService,
            TranscriptionJobService transcriptionJobService,
            @Value("${app.uploads.path}") String uploadsPath) throws Exception {
        this.lectures = lectures;
        this.courses = courses;
        this.transcriptionClient = transcriptionClient;
        this.corpusService = corpusService;
        this.transcriptionJobService = transcriptionJobService;
        this.uploadsDir = Path.of(uploadsPath).toAbsolutePath();
        Files.createDirectories(this.uploadsDir);
    }

    /** Доп. материал (не лекция): текст / файл заметки → сразу в корпус */
    public Map<String, Object> addMaterial(String courseId, String title, String text) {
        courses.requireOwned(courseId);
        if (text == null || text.isBlank()) {
            throw new IllegalArgumentException("текст материала обязателен");
        }
        String id = UUID.randomUUID().toString();
        LectureRepository.LectureRow row = new LectureRepository.LectureRow(
                id,
                courseId,
                title == null || title.isBlank() ? "Material" : title.trim(),
                "MATERIAL",
                "READY",
                text.trim(),
                null,
                Instant.now().toString());
        lectures.insert(row);
        corpusService.buildForCourse(courseId);
        return toMap(row);
    }

    public Map<String, Object> addMaterialFile(String courseId, String title, MultipartFile file) {
        if (file == null || file.isEmpty()) {
            throw new IllegalArgumentException("file обязателен");
        }
        String original = file.getOriginalFilename() == null ? "notes.txt" : file.getOriginalFilename();
        String lower = original.toLowerCase(Locale.ROOT);
        if (!(lower.endsWith(".txt") || lower.endsWith(".md") || lower.endsWith(".markdown"))) {
            throw new IllegalArgumentException("Доп. материалы: .txt или .md");
        }
        try {
            String text = new String(file.getBytes(), java.nio.charset.StandardCharsets.UTF_8);
            String name = title == null || title.isBlank() ? original : title.trim();
            return addMaterial(courseId, name, text);
        } catch (IllegalArgumentException e) {
            throw e;
        } catch (Exception e) {
            throw new IllegalStateException("Не удалось прочитать файл: " + e.getMessage(), e);
        }
    }

    public Map<String, Object> addAudio(String courseId, String title, MultipartFile file) {
        courses.requireOwned(courseId);
        if (!transcriptionClient.configured()) {
            throw new IllegalStateException("OPENROUTER_API_KEY не задан — STT недоступен. Проверь application-local.yml и перезапуск backend.");
        }
        if (file == null || file.isEmpty()) {
            throw new IllegalArgumentException("audio file обязателен");
        }
        String original = file.getOriginalFilename() == null ? "audio.bin" : file.getOriginalFilename();
        String lower = original.toLowerCase(Locale.ROOT);
        if (!(lower.endsWith(".mp3") || lower.endsWith(".m4a") || lower.endsWith(".wav") || lower.endsWith(".ogg")
                || lower.endsWith(".webm") || lower.endsWith(".mp4"))) {
            throw new IllegalArgumentException("Поддерживаются mp3/m4a/wav/ogg/webm/mp4");
        }

        String id = UUID.randomUUID().toString();
        Path dest = uploadsDir.resolve(id + "_" + sanitize(original));
        try {
            file.transferTo(dest);
        } catch (Exception e) {
            throw new IllegalStateException("Не удалось сохранить файл: " + e.getMessage(), e);
        }

        LectureRepository.LectureRow pending = new LectureRepository.LectureRow(
                id,
                courseId,
                title == null || title.isBlank() ? original : title.trim(),
                "AUDIO",
                "TRANSCRIBING",
                null,
                dest.toString(),
                Instant.now().toString());
        lectures.insert(pending);

        // Return immediately; STT runs in background
        transcriptionJobService.transcribeAsync(id, courseId, dest);
        return toMap(pending);
    }

    public List<Map<String, Object>> list(String courseId) {
        courses.requireOwned(courseId);
        return lectures.findByCourse(courseId).stream().map(this::toMap).toList();
    }

    public Map<String, Object> get(String lectureId) {
        LectureRepository.LectureRow row = lectures.findById(lectureId)
                .orElseThrow(() -> new IllegalArgumentException("Лекция не найдена"));
        courses.requireOwned(row.courseId());
        Map<String, Object> map = toMap(row);
        map.put("segments", lectures.findSegments(lectureId).stream()
                .map(s -> Map.of(
                        "startMs", s.startMs(),
                        "endMs", s.endMs(),
                        "text", s.text(),
                        "ordinal", s.ordinal()))
                .toList());
        return map;
    }

    private Map<String, Object> toMap(LectureRepository.LectureRow row) {
        Map<String, Object> map = new LinkedHashMap<>();
        map.put("id", row.id());
        map.put("courseId", row.courseId());
        map.put("title", row.title());
        map.put("sourceType", row.sourceType());
        map.put("status", row.status());
        map.put("rawText", row.rawText() == null ? "" : row.rawText());
        map.put("createdAt", row.createdAt());
        return map;
    }

    private String sanitize(String name) {
        return name.replaceAll("[^a-zA-Z0-9._-]", "_");
    }
}
