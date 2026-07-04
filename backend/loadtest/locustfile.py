"""Load test that mimics 55 students on the AdaptLearn platform.

It reproduces the real request mix: reading the dashboard / lessons (light,
frequent) plus the heavy path of starting a quiz, recording per-question
interactions, and submitting (grading + adaptive logic + DB writes).

Prep on the target VM (from backend/):
    python manage.py seed_test_students --count 55
    # open at least one unit so quizzes are accessible:
    #   管理中心 → 學習路徑 → 打開 Unit 1  (or via the shell / API)

Run from your own machine (NOT the VM — you want to load it, not share its CPU):
    pip install -r loadtest/requirements.txt
    locust -f loadtest/locustfile.py --host http://140.131.115.76

Then open http://localhost:8089 and set:
    Number of users = 55, Ramp up = 10/s.

To simulate the "everyone submits at once" spike, run headless with a short test:
    locust -f loadtest/locustfile.py --host http://140.131.115.76 \
           --headless -u 55 -r 55 -t 2m

Watch `htop` / `free -h` on the VM while it runs. Green (RPS steady, latency
flat, no failures) = fine. Rising p95 latency or failures = you hit a ceiling.
"""
import random

from locust import HttpUser, between, task

# Test accounts created by `manage.py seed_test_students`.
STUDENT_COUNT = 55
PASSWORD = 'loadtest-pw'


class Student(HttpUser):
    # Humans pause between clicks; this keeps the load realistic rather than a
    # synthetic hammer. 3-12s mirrors reading a screen before the next action.
    wait_time = between(3, 12)

    def on_start(self):
        """Log in once per simulated student and cache the JWT."""
        n = random.randint(1, STUDENT_COUNT)
        self.username = f'loadtest{n:03d}'
        self.token = None
        self.open_quiz_id = None
        with self.client.post(
            '/api/auth/login/',
            json={'username': self.username, 'password': PASSWORD},
            catch_response=True,
            name='auth/login',
        ) as resp:
            if resp.status_code == 200:
                self.token = resp.json().get('access')
            else:
                resp.failure(f'login failed: {resp.status_code}')

    @property
    def headers(self):
        return {'Authorization': f'Bearer {self.token}'} if self.token else {}

    # ---- Light, frequent reads (the bulk of real traffic) ----------------

    @task(10)
    def dashboard(self):
        if not self.token:
            return
        self.client.get('/api/learning/adaptive-path/', headers=self.headers, name='learning/adaptive-path')
        self.client.get('/api/learning/progress/', headers=self.headers, name='learning/progress')

    @task(6)
    def read_lesson(self):
        if not self.token:
            return
        lesson_id = random.randint(1, 24)  # 3 levels x 8 units
        self.client.get(f'/api/courses/lesson/{lesson_id}/', headers=self.headers,
                        name='courses/lesson/[id]')
        # material heartbeat + activity ping, as the lesson page fires them
        self.client.post('/api/learning/heartbeat/', headers=self.headers, name='learning/heartbeat')

    @task(4)
    def record_events(self):
        """Batch event upload, like the localStorage queue flush."""
        if not self.token:
            return
        batch = [{
            'event_uuid': f'{self.username}-{random.random()}',
            'event_type': random.choice(['answer_change', 'material_scroll', 'focus']),
            'page_url': 'http://loadtest/lesson.html',
            'app_version': 'loadtest',
        } for _ in range(random.randint(1, 5))]
        self.client.post('/api/learning/events/', json=batch, headers=self.headers,
                         name='learning/events (batch)')

    # ---- Heavy path: start -> submit a quiz (grading + adaptive logic) ----

    @task(2)
    def take_quiz(self):
        if not self.token:
            return
        quiz_id = random.randint(1, 24)
        with self.client.post('/api/assessments/start/', json={'quiz_id': quiz_id},
                              headers=self.headers, catch_response=True,
                              name='assessments/start') as resp:
            if resp.status_code != 201:
                # unit not open / not seeded — expected for closed units, don't count as failure
                resp.success()
                return
            data = resp.json()
        attempt_id = data.get('id')
        questions = (data.get('quiz_data') or {}).get('questions') or []
        if not attempt_id or not questions:
            return

        # Build answers for every sampled question (submit rejects partial sets).
        answers = []
        for q in questions:
            if q.get('question_type') == 'multiple_choice' and q.get('choices'):
                ans = str(random.choice(q['choices'])['id'])
            else:
                ans = 'x'
            answers.append({'question_id': q['id'], 'student_answer': ans})

        # The spike moment: everyone POSTing submit at once.
        self.client.post('/api/assessments/submit/',
                         json={'attempt_id': attempt_id, 'quiz_id': quiz_id, 'answers': answers},
                         headers=self.headers, name='assessments/submit')
