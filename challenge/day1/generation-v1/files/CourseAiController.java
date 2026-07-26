package com.ailab.course;

import com.ailab.conspect.ConspectService;
import com.ailab.qa.AskService;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/courses/{courseId}")
public class CourseAiController {

    public record AskRequest(String question) {
    }

    private final CourseService courseService;
    private final ConspectService conspectService;
    private final AskService askService;

    public CourseAiController(
            CourseService courseService,
            ConspectService conspectService,
            AskService askService) {
        this.courseService = courseService;
        this.conspectService = conspectService;
        this.askService = askService;
    }

    @GetMapping("/outline")
    public Map<String, Object> outline(@PathVariable String courseId) {
        return courseService.outline(courseId);
    }

    @PostMapping("/conspect")
    public Map<String, Object> generateConspect(@PathVariable String courseId) {
        return conspectService.generate(courseId);
    }

    @GetMapping("/conspect")
    public Map<String, Object> getConspect(@PathVariable String courseId) {
        return conspectService.latest(courseId);
    }

    @PostMapping("/ask")
    public Map<String, Object> ask(@PathVariable String courseId, @RequestBody AskRequest request) {
        return askService.ask(courseId, request.question());
    }
}
