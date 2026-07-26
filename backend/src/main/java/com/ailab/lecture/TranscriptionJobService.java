package com.ailab.lecture;

import com.ailab.corpus.CorpusService;
import com.ailab.stt.AudioChunker;
import com.ailab.stt.TranscriptionClient;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

@Service
public class TranscriptionJobService {

    private static final Logger log = LoggerFactory.getLogger(TranscriptionJobService.class);

    private final LectureRepository lectures;
    private final TranscriptionClient transcriptionClient;
    private final CorpusService corpusService;
    private final AudioChunker audioChunker;

    public TranscriptionJobService(
            LectureRepository lectures,
            TranscriptionClient transcriptionClient,
            CorpusService corpusService,
            AudioChunker audioChunker) {
        this.lectures = lectures;
        this.transcriptionClient = transcriptionClient;
        this.corpusService = corpusService;
        this.audioChunker = audioChunker;
    }

    @Async
    public void transcribeAsync(String lectureId, String courseId, Path audioPath) {
        log.info("STT start lectureId={} file={}", lectureId, audioPath);
        Path workDir = audioPath.getParent().resolve(lectureId + "_chunks");
        try {
            AudioChunker.SplitResult split = audioChunker.splitForTranscription(audioPath, workDir);
            log.info("STT parts={} chunked={}", split.parts().size(), split.chunked());

            List<String> texts = new ArrayList<>();
            List<LectureRepository.SegmentRow> allSegments = new ArrayList<>();
            int ordinal = 0;
            long offsetMs = 0;

            for (int i = 0; i < split.parts().size(); i++) {
                Path part = split.parts().get(i);
                log.info("STT part {}/{}: {}", i + 1, split.parts().size(), part.getFileName());
                TranscriptionClient.Result partResult = transcriptionClient.transcribe(part);
                if (partResult.text() != null && !partResult.text().isBlank()) {
                    texts.add(partResult.text().trim());
                }
                for (TranscriptionClient.Segment seg : partResult.segments()) {
                    allSegments.add(new LectureRepository.SegmentRow(
                            UUID.randomUUID().toString(),
                            lectureId,
                            seg.startMs() + offsetMs,
                            seg.endMs() + offsetMs,
                            seg.text(),
                            ordinal++));
                }
                // advance timeline by this part duration
                double partDur = audioChunker.probeDuration(part);
                offsetMs += Math.round(partDur * 1000);
                lectures.updateStatusAndText(
                        lectureId,
                        "TRANSCRIBING",
                        "part " + (i + 1) + "/" + split.parts().size());
            }

            String fullText = texts.stream().collect(Collectors.joining("\n\n"));
            lectures.deleteSegments(lectureId);
            for (LectureRepository.SegmentRow seg : allSegments) {
                lectures.insertSegment(seg);
            }
            // If no segments from API, synthesize coarse ones from parts text
            if (allSegments.isEmpty() && !texts.isEmpty()) {
                long cursor = 0;
                int ord = 0;
                for (int i = 0; i < texts.size(); i++) {
                    Path part = split.parts().get(i);
                    long durMs = Math.round(audioChunker.probeDuration(part) * 1000);
                    lectures.insertSegment(new LectureRepository.SegmentRow(
                            UUID.randomUUID().toString(),
                            lectureId,
                            cursor,
                            cursor + durMs,
                            texts.get(i),
                            ord++));
                    cursor += durMs;
                }
            }

            lectures.updateStatusAndText(lectureId, "READY", fullText);
            corpusService.buildForCourse(courseId);
            log.info("STT done lectureId={} chars={} segments={}",
                    lectureId, fullText.length(), allSegments.size());
        } catch (Exception e) {
            log.error("STT failed lectureId={}: {}", lectureId, e.getMessage(), e);
            lectures.updateStatusAndText(lectureId, "FAILED", e.getMessage());
        } finally {
            cleanupDir(workDir);
        }
    }

    private void cleanupDir(Path workDir) {
        try {
            if (workDir == null || !Files.isDirectory(workDir)) {
                return;
            }
            try (var stream = Files.list(workDir)) {
                stream.forEach(p -> {
                    try {
                        Files.deleteIfExists(p);
                    } catch (Exception ignored) {
                        // best-effort
                    }
                });
            }
            Files.deleteIfExists(workDir);
        } catch (Exception ignored) {
            // best-effort
        }
    }
}
