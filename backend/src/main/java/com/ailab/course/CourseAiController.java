package com.ailab.course;

import com.ailab.conspect.ConspectService;
import com.ailab.qa.AskService;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.nio.charset.StandardCharsets;
import java.util.Map;

@RestController
@RequestMapping("/api/courses/{courseId}")
public class CourseAiController {

    public record AskRequest(String question) {
    }

    private final ConspectService conspectService;
    private final AskService askService;
    private final CourseOutlineService outlineService;

    public CourseAiController(
            ConspectService conspectService,
            AskService askService,
            CourseOutlineService outlineService) {
        this.conspectService = conspectService;
        this.askService = askService;
        this.outlineService = outlineService;
    }

    @GetMapping("/outline")
    public Map<String, Object> outline(@PathVariable String courseId) {
        return outlineService.outline(courseId);
    }

    @PostMapping("/conspect")
    public Map<String, Object> generateConspect(@PathVariable String courseId) {
        return conspectService.generate(courseId);
    }

    @GetMapping("/conspect")
    public Map<String, Object> getConspect(@PathVariable String courseId) {
        return conspectService.latest(courseId);
    }

    @GetMapping("/conspect/export")
    public ResponseEntity<String> exportConspect(@PathVariable String courseId) {
        String markdown = conspectService.exportMarkdown(courseId);
        String filename = "conspect-" + courseId + ".md";
        return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"" + filename + "\"")
                .contentType(new MediaType("text", "markdown", StandardCharsets.UTF_8))
                .body(markdown);
    }

    @PostMapping("/ask")
    public Map<String, Object> ask(@PathVariable String courseId, @RequestBody AskRequest request) {
        return askService.ask(courseId, request.question());
    }
}
