# Knowbase UI smoke scenarios (Level 2)

Base URLs (local): UI `http://localhost:5173`, API `http://localhost:8081`.

Credentials: register a fresh user per run, e.g. `smoke_<timestamp>` / `smoke1234`.

---

## S1 — Register → login gate

1. Open `/login.html`
2. Register new username/password
3. Expect redirect to `/courses.html` (or land on courses list)
4. Open `/course.html` without id / or reload courses — still authenticated
5. Click logout if present → back to login

**Pass:** authenticated session after register; protected page not stuck on login.

---

## S2 — Create course → appears in list → delete

1. Login/register
2. On courses page, create course with title `Day3 Smoke Course` and subject `Testing`
3. Expect the course card/row to appear in the list (title visible; stats `курсов` increments)
4. Click **Удалить** on that row
5. Expect it gone from the list / stats back

**Pass:** create visible; delete removes it.

**UI note (Day3):** delete control is a `Удалить` button next to `Открыть` on each course row (`courses.html`).

---

## S3 — Open course → add material → build corpus signal

1. Login; create course `Day3 Material Course`
2. Open the course page
3. Paste/add a text material (e.g. short markdown note about “heap vs stack”)
4. Trigger corpus build if UI exposes it (or confirm material listed as READY)
5. Expect no error toast; material/lecture visible on page

**Pass:** material saved and visible without API error overlay.

---

## S4 — Conspect generate / export affordance

1. On a course with material + built corpus (or after S3)
2. Click generate conspect (if corpus ready) **or** verify conspect controls exist
3. If conspect exists, click «Скачать Markdown» / export
4. Expect download or non-error state

**Pass:** controls work; no uncaught UI error. If corpus empty, expect clear error message (still a pass for negative path).

---

## S5 — Ask question with citations UI

1. On course with corpus
2. Enter question e.g. `Что такое heap?`
3. Click ask
4. Expect answer area updates; citations list present **or** clear error if corpus empty

**Pass:** UI handles success or expected empty-corpus error without blank crash.

---

## Agent run protocol

For each scenario:
1. `browser_navigate` → snapshot
2. Screenshot each major step → `challenge/day3/reports/level2/screenshots/S#/NN-*.png`
3. Record PASS/FAIL + failure hypothesis in `reports/level2/REPORT.md`
