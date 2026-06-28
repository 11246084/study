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

**Apps:**
- `apps/users` — Custom `User` model extending `AbstractUser` with `role` field (`student` / `teacher` / `admin`)
- `apps/courses` — `Course`, `Lesson`, `Enrollment` models. Courses exist in 3 difficulties: `beginner`, `intermediate`, `advanced`
- `apps/assessments` — `Quiz`, `Question`, `Choice`, `QuizAttempt`, `Answer` models. Three question types: `multiple_choice`, `short_answer`, `coding`
- `apps/learning` — `AdaptiveLearningPath`, `AdaptiveRecommendation`, `LearningProgress`, `PerformanceRecord`

**API routes** (all under `/api/`):
- `/api/auth/` → register, login, profile
- `/api/courses/` → course list/detail, enroll, my courses, lesson detail
- `/api/assessments/` → quiz detail, submit, my attempts, attempt detail
- `/api/learning/` → progress, recommendations, performance, `adaptive-path/`

**Adaptive logic** lives in `apps/assessments/views.py` `SubmitAttemptView._run_adaptive_logic()`:
- Score ≥ 90 → level up (max Level 3)
- Score < 80 → level down (min Level 1)
- 80–89 → stay same level
- Creates an `AdaptiveLearningPath` record per student per unit, and an `AdaptiveRecommendation` pointing to the next unit's lesson at the calculated level
- Next unit is found by `Lesson.objects.get(course__difficulty=next_difficulty, order=next_unit)`

**Unit unlock logic** in `apps/learning/views.py` `AdaptivePathView`:
- Unit 1 is always available
- Unit N unlocks when unit N−1 has **any** `QuizAttempt` (pass not required)

**Grading logic** in `apps/assessments/views.py`:
- `multiple_choice`: match `choice.id` string
- `short_answer`: strip + lowercase exact match against `question.correct_answer`
- `coding`: compares against `Question.correct_answer` after removing whitespace and case-folding. Multiple accepted answers use a standalone `---OR---` separator. Submission is rejected when no standard answer is configured.

### Frontend (`frontend/`)

Vanilla HTML/CSS/JS — no framework, no build tool.

**Key files:**
- `js/api.js` — all API calls; `apiFetch()` handles JWT + auto-refresh; `AuthAPI`, `CoursesAPI`, `LearningAPI` namespaces
- `js/main.js` — navbar init (logo + logout button only; no nav links for students)
- `index.html` — the dashboard; unauthenticated users are redirected to `register.html`; shows 8 unit cards via `/api/learning/adaptive-path/`
- `lesson.html` — reads `lesson_id` from query string, fetches lesson content and quiz list
- `quiz.html` — renders questions by type (radio for MC, text input for short_answer, dark textarea for coding), submits to `/api/assessments/submit/`
- `quiz-result.html` — shows attempt result and next-unit recommendation

**Auth:** JWT tokens stored in `localStorage` (`access_token`, `refresh_token`). On 401, `apiFetch` auto-refreshes; on failure, redirects to `/register.html`.

**courses.html** is restricted to teachers/admins — the page checks `profile.role` and redirects students to `/`.

### Data Seeding (`apps/courses/management/commands/seed_data.py`)

- Creates 3 courses (beginner/intermediate/advanced), each with 8 lessons and 8 quizzes
- Beginner → 10 `multiple_choice` questions per quiz (with `Choice` records)
- Intermediate → 10 `short_answer` questions per quiz (`correct_answer` field on `Question`)
- Advanced → 10 `coding` questions per quiz; every item has at least one exact accepted answer
- Active question banks live in `curriculum_questions.py` (8 units × 10 questions per level); legacy banks remain in `seed_data.py` only for history.
- Curriculum materials are version-controlled under `frontend/assets/materials/`; `seed_data` updates existing lesson titles, content, and the 180-minute half-day duration.
- Current unit order follows the four-day schedule: fundamentals/I-O, conditionals, loops/algorithms, loop practice, list/string, list/string practice, functions, recursion/dictionaries.
- To re-seed after schema changes: delete quizzes for affected difficulty in the shell, then re-run `seed_data`

## Adaptive Recommendation Logic (needs 1 & 4)

After quiz submission, `_run_adaptive_logic()` runs two independent paths:

**Vertical path (learning progression):** Always updates `AdaptiveLearningPath` for `next_unit`:
- score ≥ 90 → next unit level up (max 3)
- score < 80 → next unit level down (min 1)
- 80–89 → next unit same level

**Horizontal path (recommendation card):** Creates one `AdaptiveRecommendation` per quiz:
| Score | Current Level | Recommendation |
|-------|--------------|----------------|
| ≥ 90  | < 3          | Same unit, level + 1 ("挑戰進階") |
| ≥ 90  | = 3          | Next unit (can't go higher) |
| < 80  | > 1          | Same unit, level − 1 ("補救複習") |
| < 80  | = 1          | Next unit at level 1 (can't go lower) |
| 80–89 | any          | Next unit at same level |

After all 8 units completed: `_recommend_weakest_units()` creates review recommendations for the 3 lowest-scoring units.

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
