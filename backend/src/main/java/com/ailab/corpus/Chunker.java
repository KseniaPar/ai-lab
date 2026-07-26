package com.ailab.corpus;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import java.util.ArrayList;
import java.util.List;

@Component
public class Chunker {

    public record TextChunk(String text, Long startMs, Long endMs, int ordinal) {
    }

    private final int chunkSize;
    private final int overlap;

    public Chunker(
            @Value("${app.corpus.chunk-size}") int chunkSize,
            @Value("${app.corpus.chunk-overlap}") int overlap) {
        this.chunkSize = Math.max(200, chunkSize);
        this.overlap = Math.max(0, Math.min(overlap, chunkSize / 2));
    }

    public List<TextChunk> chunkPlain(String text) {
        if (text == null || text.isBlank()) {
            return List.of();
        }
        String normalized = text.replace("\r\n", "\n").trim();
        List<TextChunk> result = new ArrayList<>();
        int ordinal = 0;
        int i = 0;
        while (i < normalized.length()) {
            int end = Math.min(normalized.length(), i + chunkSize);
            if (end < normalized.length()) {
                int space = normalized.lastIndexOf(' ', end);
                if (space > i + chunkSize / 2) {
                    end = space;
                }
            }
            String piece = normalized.substring(i, end).trim();
            if (!piece.isBlank()) {
                result.add(new TextChunk(piece, null, null, ordinal++));
            }
            if (end >= normalized.length()) {
                break;
            }
            i = Math.max(i + 1, end - overlap);
        }
        return result;
    }

    public List<TextChunk> chunkSegments(List<SegmentInput> segments) {
        if (segments == null || segments.isEmpty()) {
            return List.of();
        }
        List<TextChunk> result = new ArrayList<>();
        StringBuilder buf = new StringBuilder();
        Long startMs = null;
        Long endMs = null;
        int ordinal = 0;
        for (SegmentInput seg : segments) {
            if (buf.isEmpty()) {
                startMs = seg.startMs();
            }
            if (!buf.isEmpty()) {
                buf.append(' ');
            }
            buf.append(seg.text().trim());
            endMs = seg.endMs();
            if (buf.length() >= chunkSize) {
                result.add(new TextChunk(buf.toString().trim(), startMs, endMs, ordinal++));
                buf.setLength(0);
                startMs = null;
                endMs = null;
            }
        }
        if (!buf.isEmpty()) {
            result.add(new TextChunk(buf.toString().trim(), startMs, endMs, ordinal));
        }
        return result;
    }

    public record SegmentInput(long startMs, long endMs, String text) {
    }
}
