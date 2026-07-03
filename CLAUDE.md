# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**程式設計適性學習輔助系統 (AdaptLearn)** — A formative-assessment-driven adaptive learning platform for Python programming. Students are automatically routed between three difficulty levels after each unit quiz.

## Development Setup

### Backend (Django)

```bash
# All backend commands run from the backend/ directory
cd backend

# Start the server (also serves the frontend at http://127.0.0.1:8000/)
python manage.py runserver

# Apply migrations
python manage.py migrate

# Seed all course/quiz data (run after clearing or first setup)
python manage.py seed_data

# Open Django shell
python manage.py shell

# Create a superuser
python manage.py createsuperuser
```

### Database (MySQL)

```bash
# Start MySQL (Windows)
/c/Program\ Files/MySQL/MySQL\ Server\ 8.0/bin/mysqld --console

# Create DB if missing (run in MySQL client)
CREATE DATABASE study_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Environment variables are read via `python-decouple` from a `.env` file in `backend/`:
```
DB_NAME=study_db
DB_USER=root
DB_PASSWORD=your_password
SECRET_KEY=...
```

### Frontend

The frontend is **served directly by Django** at `http://127.0.0.1:8000/` — no separate build step or dev server needed. All HTML files in `frontend/` are accessible as static files via Django's `views.static.serve`.

## Architecture

### Backend (`backend/`)

Django 5.2 + DRF 3.15.2, JWT auth via `djangorestframework-simplejwt`.

**Apps（資料庫分四區：身分／課程內容／學習狀態／研究原始層）:**
- `apps/users` — Custom `User` model extending `AbstractUser` with `role` field (`student` / `teacher` / `admin`); `LoginEvent`、`DataChangeAudit`（稽核）
- `apps/courses` — `Course`, `Lesson`. Courses exist in 3 difficulties: `beginner`, `intermediate`, `advanced`（沒有選課概念，Enrollment 已移除）
- `apps/assessments` — `Quiz`, `Question`, `Choice`, `QuizAttempt`, `Answer`, `QuestionInteraction`. Question types: `multiple_choice`, `true_false`, `short_answer`, `coding`, `fill_blank`
- `apps/learning` — `AdaptiveLearningPath`, `AdaptiveRecommendation`, `LearningProgress`, `StudentUnitSummary`（給人看的彙總：一列＝學生×單元）, `UnitRelease`（老師手動開放單元）, `StudySession` + `StudentEvent`（研究原始層，唯讀）
- 彙總層由交卷/教材心跳即時更新，也可 `python manage.py rebuild_unit_summaries` 從原始資料整表重算
- **研究事件埋點慣例**（`apps/learning/tracking.py`）：所有 `StudentEvent` 建立點都套用 `event_context(request)` — `occurred_at` 存用戶端時間（`client_occurred_at`，時鐘異常回退伺服器時間）、自動繫結活躍 `StudySession`、`metadata.tab_uuid` 區分分頁；`answer_change` 事件的 `metadata.answer` 保存當次答案全文（可重建修改歷程）。前端 `api.js` 的 `eventStamp()` 產生時間戳＋tab；`recordEvent` 走 localStorage 佇列批次上傳（失敗保留、開頁補送、後端以 event_uuid 去重）。跑報表前先 `python manage.py close_stale_sessions` 補關逾時時段。

**API routes** (all under `/api/`):
- `/api/auth/` → register, login, profile
- `/api/courses/` → course list/detail, lesson detail
- `/api/assessments/` → quiz detail, start, submit, my attempts, attempt detail
- `/api/learning/` → progress, recommendations, `adaptive-path/`, `unit-release/`（老師開關單元，GET 列表／POST 切換）

**Adaptive logic** lives in `apps/assessments/views.py` `SubmitAttemptView._run_adaptive_logic()`:
- Score ≥ 80 → level up (max Level 3)
- Score < 60 → level down (min Level 1)
- 60–79 → stay same level
- Creates an `AdaptiveLearningPath` record per student per unit, and an `AdaptiveRecommendation` pointing to the next unit's lesson at the calculated level
- Next unit is found by `Lesson.objects.get(course__difficulty=next_difficulty, order=next_unit)`

**Unit unlock logic**（老師手動控制；4 天課程，每天下課後老師開放當天單元）:
- `UnitRelease` 表（8 列）決定單元是否對學生開放；`can_access_lesson()` 與 `AdaptivePathView` 都以 `is_open` 為準
- **不再**依「前一單元有作答」自動解鎖；已作答的單元照樣顯示「已完成」
- 開關 UI 在管理中心「學習路徑」頁（index.html?admin_mode=1）每張單元卡下方；seed 預設全部關閉
- 適性「等級」邏輯不變：交卷後仍自動計算並指定下一單元 Level

**Grading logic** in `apps/assessments/views.py`:
- `multiple_choice`: match `choice.id` string
- `short_answer`: strip + lowercase exact match against `question.correct_answer`
- `coding`: compares against `Question.correct_answer` after removing whitespace and case-folding. Multiple accepted answers use a standalone `---OR---` separator.
- `fill_blank`（Level 3 主力題型）: 題目內文以 `__1__`、`__2__` 標記空格；`correct_answer` 一行對應一格，同格多解以 `|||` 分隔。學生答案以換行分格提交，逐格比對（忽略空白、保留大小寫），按答對格數比例給分。出題紀律：空格只挖答案唯一的位置（運算子、關鍵字、方法名、參數），不挖變數名或整行。

### Frontend (`frontend/`)

Vanilla HTML/CSS/JS — no framework, no build tool.

**Key files:**
- `js/api.js` — all API calls; `apiFetch()` handles JWT + auto-refresh; `AuthAPI`, `CoursesAPI`, `LearningAPI` namespaces
- `js/main.js` — navbar init (logo + logout button only; no nav links for students)
- `index.html` — the dashboard; unauthenticated users are redirected to `register.html`; shows 8 unit cards via `/api/learning/adaptive-path/`
- `lesson.html` — reads `lesson_id` from query string, fetches lesson content and quiz list
- `quiz.html` — renders questions by type (radio for MC, text input for short_answer, dark textarea for coding, inline inputs inside the code block for fill_blank), submits to `/api/assessments/submit/`
- `admin-shell.html` — 管理中心外殼；資料管理側欄分「日常區」與「研究原始資料（唯讀）」兩區
- `admin-dashboard.html` — 研究儀表板，圖表使用 Chart.js（CDN）；render 函式先回傳 `<canvas>`，`mountCharts()` 在 innerHTML 寫入後實例化
- `quiz-result.html` — shows attempt result and next-unit recommendation

**Auth:** JWT tokens stored in `localStorage` (`access_token`, `refresh_token`). On 401, `apiFetch` auto-refreshes; on failure, redirects to `/register.html`.

**courses.html** is restricted to teachers/admins — the page checks `profile.role` and redirects students to `/`.

### Data Seeding (`apps/courses/management/commands/seed_data.py`)

- Creates 3 courses (beginner/intermediate/advanced), each with 8 lessons and 8 quizzes; also seeds the 8 `UnitRelease` switches (default closed — open them from 管理中心)
- Each unit/level owns a 100-question bank; each attempt securely samples 10 questions server-side.
- Beginner banks use `multiple_choice`, intermediate banks use `short_answer`, and advanced banks use `fill_blank`（程式填空，`FILL_BLANK_QUESTIONS`）.
- Active question banks live in `curriculum_questions.py` (8 units × 100 questions per level); legacy banks remain in `seed_data.py` only for history.
- `QuizAttempt.selected_question_ids` persists the sampled set. Submission and interaction APIs reject any question outside that set; summary endpoints never expose the full bank.
- Curriculum materials are version-controlled under `frontend/assets/materials/`; `seed_data` updates existing lesson titles, content, and the 180-minute half-day duration.
- Current unit order follows the four-day schedule: fundamentals/I-O, conditionals, loops/algorithms, loop practice, list/string, list/string practice, functions, recursion/dictionaries.
- To re-seed after schema changes: delete quizzes for affected difficulty in the shell, then re-run `seed_data`

## Adaptive Recommendation Logic (needs 1 & 4)

After quiz submission, `_run_adaptive_logic()` runs two independent paths:

**Vertical path (learning progression):** Always updates `AdaptiveLearningPath` for `next_unit`:
- score ≥ 80 → next unit level up (max 3)
- score < 60 → next unit level down (min 1)
- 60–79 → next unit same level

**Horizontal path (recommendation card):** Creates one `AdaptiveRecommendation` per quiz:
| Score | Current Level | Recommendation |
|-------|--------------|----------------|
| ≥ 80  | < 3          | Same unit, level + 1 ("挑戰進階") |
| ≥ 80  | = 3          | Next unit (can't go higher) |
| < 60  | > 1          | Same unit, level − 1 ("補救複習") |
| < 60  | = 1          | Next unit at level 1 (can't go lower) |
| 60–79 | any          | Next unit at same level |

After all 8 units completed: `_recommend_weakest_units()` creates review recommendations for 3 units, ordered by lowest current level first and then lowest score.

`next_lesson_data` now includes `is_same_unit: bool` so the frontend can differentiate "挑戰進階" from "前往下一單元".

**Dashboard unit cards (need 4 — dual learning path):**
- Each card shows the adaptive-path recommended lesson as the primary button
- Level switcher row shows 3 small buttons (Level 1/2/3), current level highlighted
- All 3 levels are always accessible regardless of the adaptive path level
- `AdaptivePathView` returns `all_levels: {1: lesson_id, 2: lesson_id, 3: lesson_id}` per unit

## Lesson Page Unit Restrictions (need 3)

`lesson.html` uses `/api/learning/adaptive-path/` (not same-course lessons) for:
- **Left sidebar (COURSE UNITS):** Shows all 8 units; locked units shown as greyed-out, non-clickable
- **Bottom "next unit" button:** Hidden if next unit's `status === 'locked'`
- **Bottom "prev unit" button:** Always shown if unit > 1
- Sidebar links use `lesson_id` from `adaptive-path` (accounts for each unit's current level)
- Active unit in sidebar is matched by `unit_number === lesson.order` (not lesson_id), so students reviewing supplementary levels still see the correct active state

## Key Constraints

- The platform has exactly **8 units** and **3 levels** — hardcoded in multiple places (`UNIT_TITLES` arrays, `unit_number > 8` guard in adaptive logic, `range(1, 9)` in `AdaptivePathView`)
- `Lesson.order` (1–8) is used as the unit number throughout the adaptive system — don't change ordering
- `Course.difficulty` strings (`beginner`/`intermediate`/`advanced`) map to levels 1/2/3 everywhere — keep consistent
- `CORS_ALLOW_ALL_ORIGINS = True` is set for development; frontend and backend run on the same origin (port 8000) so CORS is not actually needed
