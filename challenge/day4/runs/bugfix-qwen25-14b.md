# bugfix — qwen2.5:14b
seconds: 66.1
eval_count: 288
prompt_eval_count: 427

---

### Cause
В методе `AskService.formatTimestamp` используется неверная логика для форматирования времени в строку "минуты:секунды". Возможно, там используется деление на 60 секунд вместо правильного вычисления минут и секунд.

### Fix
Нужно изменить метод `AskService.formatTimestamp`, чтобы он правильно рассчитывал количество минут и секунд из миллисекунд. Пример исправленного кода:

```java
public static String formatTimestamp(long milliseconds) {
    long minutes = (milliseconds / 1000) / 60;
    long seconds = (milliseconds / 1000) % 60;
    return String.format("%d:%02d", minutes, seconds);
}
```

### Verification
Для проверки правильности исправления можно использовать тесты:

```java
@Test
public void testFormatTimestamp() {
    assertEquals("1:05", AskService.formatTimestamp(65000));
    assertEquals("3:45", AskService.formatTimestamp(225000));
}
```

### Blast radius
Изменение затрагивает только метод `formatTimestamp` в классе `AskService`. Это локальное изменение, которое не влияет на другие части приложения.
