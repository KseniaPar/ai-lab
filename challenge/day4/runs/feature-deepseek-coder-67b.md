# feature — deepseek-coder:6.7b
seconds: 142.3
eval_count: 1092
prompt_eval_count: 599

---

Создадим два новых сервиса `SourceSummaryService` и `CourseSourcesService`, а также метод в контроллере `CourseAiController` для обработки запроса. 

1. Создаем класс SourceSummaryService:
```java
@Service
public class SourceSummaryService {
    private final CourseSourcesService courseSourcesService;
    
    @Autowired
    public SourceSummaryService(CourseSourcesService courseSourcesService) {
        this.courseSourcesService = courseSourcesService;
   }

    public Map<String, Object> getSourceSummary(int courseId) {
        List<Source> sources = courseSourcesService.getAllByCourseId(courseId);
        
        long audioCount = sources.stream().filter(source -> source.getSourceType() == SourceType.AUDIO).count();
        long materialCount = sources.stream().filter(source -> source.getSourceType() == SourceType.MATERIAL).count();
        long readyCount = sources.stream().filter(Source::isReady).count();
        
        Map<String, Object> summary = new LinkedHashMap<>();
        summary.put("audioCount", audioCount);
        summary.put("materialCount", materialCount);
        summary.put("readyCount", readyCount);
        
        return summary;
    }
}
```
2. Создаем класс CourseSourcesService:
```java
@Service
public class CourseSourcesService {
    private final SourceRepository sourceRepository;
    
    @Autowired
    public CourseSourcesService(SourceRepository sourceRepository) {
        this.sourceRepository = sourceRepository;
    }
    
    public List<Source> getAllByCourseId(int courseId) {
        return sourceRepository.findByCourseId(courseId);
    }
}
```
3. Создаем класс CourseAiController:
```java
@RestController
@RequestMapping("/api/courses/{courseId}/source-summary")
public class CourseAiController {
    private final SourceSummaryService sourceSummaryService;
    
    @Autowired
    public CourseAiController(SourceSummaryService sourceSummaryService) {
        this.sourceSummaryService = sourceSummaryService;
    }
    
    @GetMapping
    public ResponseEntity<Map<String, Object>> getSourceSummary(@PathVariable int courseId) {
        requireOwned(courseId); // проверяем владение курсом
        
        Map<String, Object> summary = sourceSummaryService.getSourceSummary(courseId);
        return ResponseEntity.ok(summary);
    }
}
```
4. Добавляем метод requireOwned в CourseAiController:
```java
private void requireOwned(int courseId) {
    // проверяем владение курсом, если не владеет - бросаем SecurityException
}
```
5. Создаем интерфейс SourceRepository для доступа к данным источников:
```java
public interface SourceRepository extends JpaRepository<Source, Integer> {
    List<Source> findByCourseId(int courseId);
}
```
6. Создаем класс Course для соответствия схеме JSON:
```java
record Course(int id, String title, String subject) {}
```
7. Создаем класс Source для соответствия схеме JSON:
```java
@Entity
class Source {
    @Id
    private int id;
    
    private String title;
    
    @Enumerated(EnumType.STRING)
    private SourceType sourceType;
    
    private boolean ready;
    
    // getters and setters...
}
```
8. Создаем enum SourceType для соответствия схеме JSON:
```java
public enum SourceType {
    AUDIO, MATERIAL
}
```
9. Добавьте эти новые классы в пакет `com.ailab.knowbase`.

Таким образом, мы создали два отдельных сервиса для получения сводной информации о источниках курсов (SourceSummaryService) и основной службе по работе с источниками (CourseSourcesService). Метод getSourceSummary в CourseAiController возвращает JSON, соответствующий контракту.

