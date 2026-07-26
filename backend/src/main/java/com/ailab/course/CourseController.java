package com.ailab.course;

import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/courses")
public class CourseController {

    public record CreateCourseRequest(String title, String subject) {
    }

    private final CourseService courseService;

    public CourseController(CourseService courseService) {
        this.courseService = courseService;
    }

    @PostMapping
    public Map<String, Object> create(@RequestBody CreateCourseRequest request) {
        return courseService.create(request.title(), request.subject());
    }

    @GetMapping
    public List<Map<String, Object>> list() {
        return courseService.listMine();
    }

    @GetMapping("/{id}")
    public Map<String, Object> get(@PathVariable String id) {
        return courseService.get(id);
    }

    @DeleteMapping("/{id}")
    public Map<String, String> delete(@PathVariable String id) {
        courseService.delete(id);
        return Map.of("status", "deleted");
    }
}
