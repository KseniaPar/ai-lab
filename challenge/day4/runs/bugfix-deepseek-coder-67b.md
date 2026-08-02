# bugfix — deepseek-coder:6.7b
seconds: 49.4
eval_count: 427
prompt_eval_count: 557

---

Cause: В методе formatTimestamp в классе AskService происходит округление времени до целого числа, а не до двух знаков после запятой. Это может привести к неправильному форматированию отформатированного временного интервала.

Fix: В методе formatTimestamp в классе AskService можно добавить округление числа до двух знаков после запятой, используя Math.round() функцию.

Verification: Для проверки фикса необходимо вызвать метод formatTimestamp с аргументом 65000ms и сравнить результат с ожидаемым "1:5".

Blast radius: Этот баг может повлиять на работу всего приложения, если другие части кода используют метод formatTimestamp. Однако в данном случае фикс будет единственным действием и он не должен повлиять на работу остального приложения.

```java
public String formatTimestamp(long milliseconds) {
    long seconds = (milliseconds / 1000) % 60;
    long minutes = (milliseconds / (1000 * 60)) % 60;
    
    return String.format("%d:%02d", minutes, Math.round(seconds));
}
```

Теперь метод formatTimestamp должен правильно форматировать время в секундах и минутах.

