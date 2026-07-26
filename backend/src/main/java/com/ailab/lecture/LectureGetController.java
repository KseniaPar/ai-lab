package com.ailab.lecture;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
@RequestMapping("/api/lectures")
public class LectureGetController {

    private final LectureService lectureService;

    public LectureGetController(LectureService lectureService) {
        this.lectureService = lectureService;
    }

    @GetMapping("/{id}")
    public Map<String, Object> get(@PathVariable String id) {
        return lectureService.get(id);
    }
}
