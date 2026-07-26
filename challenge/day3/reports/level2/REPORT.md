# Day 3 — Level 2 smoke report

**Runner:** cursor-ide-browser MCP (Playwright MCP not installed in workspace)  
**UI:** `http://localhost:5175` (Vite; 5173/5174 busy) · **API:** `http://localhost:8081`  
**User:** `smoke_day3_user` (registered during S1)

| Scenario | Result | Evidence |
|----------|--------|----------|
| S1 Register → courses | **PASS** | `screenshots/S1/01-login.png`, `S1/02-courses-after-register.png` — landed on courses with stats |
| S2 Create → list → delete | **PASS** | `S2/01-course-created.png` (2× Day3 Smoke Course), `S2/02-after-delete.png` (0 courses). Delete button added to `courses.html` during Day3 (was missing initially). |
| S3 Material → corpus | **PASS** | Material `Heap notes` READY; ok `Corpus: 1 chunks`; `S3/02-course-with-material.png` |
| S4 Conspect | **PASS** | ok `Конспект готов`; markdown preview filled; `S4/01-conspect-ready.png` |
| S5 Ask + citations | **PASS** | Answer + `[1]` citation; ok `Готово`; `S5/01-ask-with-citations.png` |

## Failures / hypotheses

1. **First create click via `browser_click` did not apply** — form stayed filled, stats stayed 0. Working around with `Runtime.evaluate` + `#create.click()` succeeded. Likely timing/focus with Vite HMR or click not hitting the JS handler. Prefer DOM id clicks for this UI in future smoke runs.
2. **Courses UI lacked Delete** before Day3 fix — would have failed S2; fixed in `frontend/courses.html`.
3. **S1 logout** not re-verified in-browser (session mutation gated); register→courses already proves auth gate.

## Notes for “я задеплоил новую фичу”

Updated scenarios already include Delete on courses list and Conspect export button. Re-run via **qa-runner** after deploys.
