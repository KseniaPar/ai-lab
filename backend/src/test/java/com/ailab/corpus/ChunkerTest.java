package com.ailab.corpus;

import org.junit.jupiter.api.Test;

import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

class ChunkerTest {

    @Test
    void chunksPlainText() {
        Chunker chunker = new Chunker(100, 20);
        String text = "A".repeat(250);
        List<Chunker.TextChunk> chunks = chunker.chunkPlain(text);
        assertFalse(chunks.isEmpty());
        assertTrue(chunks.size() >= 2);
    }

    @Test
    void emptyTextReturnsEmpty() {
        Chunker chunker = new Chunker(800, 120);
        assertTrue(chunker.chunkPlain("").isEmpty());
    }

    @Test
    void whitespaceOnlyReturnsEmpty() {
        Chunker chunker = new Chunker(800, 120);
        assertTrue(chunker.chunkPlain("   \n\t  ").isEmpty());
    }

    @Test
    void chunkSegmentsMergesShortSegmentsBySize() {
        // effective chunkSize is max(200, requested)
        Chunker chunker = new Chunker(200, 0);
        String a = "A".repeat(80);
        String b = "B".repeat(80);
        String c = "C".repeat(80);
        String d = "D".repeat(80);
        List<Chunker.SegmentInput> segments = List.of(
                new Chunker.SegmentInput(0, 1000, a),
                new Chunker.SegmentInput(1000, 2000, b),
                new Chunker.SegmentInput(2000, 3000, c),
                new Chunker.SegmentInput(3000, 4000, d));
        List<Chunker.TextChunk> chunks = chunker.chunkSegments(segments);
        // after 3rd segment buf length >= 200 → flush; 4th alone → 2 chunks
        assertEquals(2, chunks.size());
        assertTrue(chunks.get(0).text().startsWith(a));
        assertTrue(chunks.get(0).text().contains(c));
        assertEquals(0L, chunks.get(0).startMs());
        assertEquals(3000L, chunks.get(0).endMs());
        assertEquals(d, chunks.get(1).text());
        assertEquals(3000L, chunks.get(1).startMs());
        assertEquals(4000L, chunks.get(1).endMs());
    }
}
