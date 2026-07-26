package com.ailab.corpus;

import org.junit.jupiter.api.Test;

import java.util.List;

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
}
