# Knowbase (ai-lab)

Личная платформа знаний для подготовки к экзамену.

**Flow:** аудио лекция → STT → корпус (+ доп. материалы) → конспект → Q&A с цитатами.

## Стек

- Backend: Java 17, Spring Boot 3.4, SQLite, JWT, Spring AI (OpenRouter)
- Frontend: Vite + vanilla JS
- STT: OpenRouter Whisper

## Быстрый старт

```powershell
# 1. API key
$env:OPENROUTER_API_KEY = "sk-or-v1-..."

# 2. Backend
cd backend
# если mvn нет в PATH — используйте путь к Maven, например из llm-chat-app\.tools
mvn spring-boot:run

# 3. Frontend (другой терминал)
cd frontend
npm install
npm run dev
```

- UI: http://localhost:5173  
- API: http://localhost:8081  

## Основные API

| Method | Path |
|--------|------|
| GET | `/api/health` |
| POST | `/api/auth/register`, `/api/auth/login` |
| CRUD | `/api/courses` |
| POST | `/api/courses/{id}/lectures` (multipart audio → STT) |
| POST | `/api/courses/{id}/materials` (текст доп. материала) |
| POST | `/api/courses/{id}/materials/file` (`.txt` / `.md`) |
| POST | `/api/courses/{id}/corpus/build` |
| GET | `/api/courses/{id}/outline` |
| GET | `/api/courses/{id}/source-summary` |
| POST/GET | `/api/courses/{id}/conspect` |
| GET | `/api/courses/{id}/conspect/export` (Markdown download) |
| POST | `/api/courses/{id}/ask` |
| GET | `/api/stats` |

## Демо

1. Зарегистрируйтесь в UI  
2. Создайте курс  
3. Загрузите короткое аудио лекции **или** доп. материал (`.txt` / заметка)  
4. Сгенерируйте конспект / задайте вопрос  

## Репозиторий

Часть **AI Advent Challenge Advanced**. Ветки челленджа (`day1`…) — отдельно, после стабилизации `main`.
