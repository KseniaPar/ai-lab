package com.ailab.corpus;

import com.ailab.lecture.LectureRepository;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Comparator;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Collectors;

@Service
public class CorpusService {

    private final ChunkRepository chunks;
    private final LectureRepository lectures;
    private final Chunker chunker;
    private final int topK;

    public CorpusService(
            ChunkRepository chunks,
            LectureRepository lectures,
            Chunker chunker,
            @Value("${app.corpus.top-k}") int topK) {
        this.chunks = chunks;
        this.lectures = lectures;
        this.chunker = chunker;
        this.topK = topK;
    }

    public Map<String, Object> buildForCourse(String courseId) {
        chunks.deleteByCourse(courseId);
        int total = 0;
        for (LectureRepository.LectureRow lecture : lectures.findByCourse(courseId)) {
            if (!"READY".equals(lecture.status()) || lecture.rawText() == null || lecture.rawText().isBlank()) {
                continue;
            }
            List<Chunker.TextChunk> textChunks;
            List<LectureRepository.SegmentRow> segments = lectures.findSegments(lecture.id());
            if (!segments.isEmpty()) {
                textChunks = chunker.chunkSegments(segments.stream()
                        .map(s -> new Chunker.SegmentInput(s.startMs(), s.endMs(), s.text()))
                        .toList());
            } else {
                textChunks = chunker.chunkPlain(lecture.rawText());
            }
            for (Chunker.TextChunk tc : textChunks) {
                chunks.insert(new ChunkRepository.ChunkRow(
                        UUID.randomUUID().toString(),
                        lecture.id(),
                        courseId,
                        tc.ordinal(),
                        tc.text(),
                        tc.startMs(),
                        tc.endMs()));
                total++;
            }
        }
        return Map.of("courseId", courseId, "chunkCount", total);
    }

    public List<ChunkRepository.ChunkRow> retrieve(String courseId, String query) {
        List<ChunkRepository.ChunkRow> all = chunks.findByCourse(courseId);
        if (all.isEmpty()) {
            return List.of();
        }
        Set<String> terms = tokenize(query);
        if (terms.isEmpty()) {
            return all.stream().limit(topK).toList();
        }
        record Scored(ChunkRepository.ChunkRow chunk, int score) {
        }
        List<Scored> scored = new ArrayList<>();
        for (ChunkRepository.ChunkRow chunk : all) {
            Set<String> chunkTerms = tokenize(chunk.text());
            int score = 0;
            for (String term : terms) {
                if (chunkTerms.contains(term)) {
                    score++;
                }
            }
            if (score > 0) {
                scored.add(new Scored(chunk, score));
            }
        }
        scored.sort(Comparator.comparingInt(Scored::score).reversed());
        if (scored.isEmpty()) {
            return all.stream().limit(topK).toList();
        }
        return scored.stream().limit(topK).map(Scored::chunk).toList();
    }

    public String corpusPreview(String courseId, int maxChars) {
        String joined = chunks.findByCourse(courseId).stream()
                .map(ChunkRepository.ChunkRow::text)
                .collect(Collectors.joining("\n\n"));
        if (joined.length() <= maxChars) {
            return joined;
        }
        return joined.substring(0, maxChars) + "\n…";
    }

    private Set<String> tokenize(String text) {
        if (text == null || text.isBlank()) {
            return Set.of();
        }
        return Arrays.stream(text.toLowerCase(Locale.ROOT).split("[^\\p{L}\\p{N}]+"))
                .filter(t -> t.length() > 2)
                .collect(Collectors.toCollection(HashSet::new));
    }
}
