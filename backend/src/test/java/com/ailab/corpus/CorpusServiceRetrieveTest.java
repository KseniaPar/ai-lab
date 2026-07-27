package com.ailab.corpus;

import com.ailab.lecture.LectureRepository;
import org.junit.jupiter.api.Test;

import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

class CorpusServiceRetrieveTest {

    @Test
    void blankQueryReturnsEmptyWithoutLookingUpChunks() {
        ChunkRepository chunks = mock(ChunkRepository.class);
        LectureRepository lectures = mock(LectureRepository.class);
        Chunker chunker = mock(Chunker.class);
        CorpusService service = new CorpusService(chunks, lectures, chunker, 6);

        assertTrue(service.retrieve("c1", "   ").isEmpty());
        assertTrue(service.retrieve("c1", null).isEmpty());
        assertTrue(service.retrieve("c1", "").isEmpty());
        verify(chunks, never()).findByCourse("c1");
    }

    @Test
    void nonBlankQueryStillRetrieves() {
        ChunkRepository chunks = mock(ChunkRepository.class);
        LectureRepository lectures = mock(LectureRepository.class);
        Chunker chunker = mock(Chunker.class);
        when(chunks.findByCourse("c1")).thenReturn(List.of(
                new ChunkRepository.ChunkRow("ch1", "l1", "c1", 0, "алгебра матрицы", null, null)));
        CorpusService service = new CorpusService(chunks, lectures, chunker, 6);

        List<ChunkRepository.ChunkRow> found = service.retrieve("c1", "матрицы");
        assertEquals(1, found.size());
        assertEquals("ch1", found.get(0).id());
    }
}
