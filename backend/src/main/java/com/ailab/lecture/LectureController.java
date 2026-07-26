package com.ailab.lecture;

import com.ailab.corpus.CorpusService;
import com.ailab.course.CourseService;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/courses/{courseId}")
public class LectureController {

    public record MaterialRequest(String title, String text) {
    }

    private final LectureService lectureService;
    private final CourseService courseService;
    private final CorpusService corpusService;

    public LectureController(
            LectureService lectureService,
            CourseService courseService,
            CorpusService corpusService) {
        this.lectureService = lectureService;
        this.courseService = courseService;
        this.corpusService = corpusService;
    }

    /** Лекция: только аудио → STT */
    @PostMapping(value = "/lectures", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public Map<String, Object> addAudio(
            @PathVariable String courseId,
            @RequestParam(value = "title", required = false) String title,
            @RequestParam("file") MultipartFile file) {
        return lectureService.addAudio(courseId, title, file);
    }

    @GetMapping("/lectures")
    public List<Map<String, Object>> list(@PathVariable String courseId) {
        return lectureService.list(courseId);
    }

    /** Доп. материалы: текст или .txt/.md файл */
    @PostMapping(value = "/materials", consumes = MediaType.APPLICATION_JSON_VALUE)
    public Map<String, Object> addMaterialText(
            @PathVariable String courseId,
            @RequestBody MaterialRequest request) {
        return lectureService.addMaterial(courseId, request.title(), request.text());
    }

    @PostMapping(value = "/materials/file", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public Map<String, Object> addMaterialFile(
            @PathVariable String courseId,
            @RequestParam(value = "title", required = false) String title,
            @RequestParam("file") MultipartFile file) {
        return lectureService.addMaterialFile(courseId, title, file);
    }

    @PostMapping("/corpus/build")
    public Map<String, Object> rebuildCorpus(@PathVariable String courseId) {
        courseService.requireOwned(courseId);
        return corpusService.buildForCourse(courseId);
    }
}
