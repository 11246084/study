from rest_framework.test import APITestCase

from apps.courses.models import Course, Lesson
from apps.users.models import User
from .models import AdaptiveLearningPath, LearningProgress, StudentEvent
import uuid


class AdaptiveLevelThresholdTests(APITestCase):
    def test_level_changes_at_new_score_boundaries(self):
        determine = AdaptiveLearningPath.determine_next_level

        self.assertEqual(determine(2, 80), 3)
        self.assertEqual(determine(2, 79), 2)
        self.assertEqual(determine(2, 60), 2)
        self.assertEqual(determine(2, 59), 1)
        self.assertEqual(determine(3, 100), 3)
        self.assertEqual(determine(1, 0), 1)


class ActivityValidationTests(APITestCase):
    def setUp(self):
        self.student = User.objects.create_user(username='student', password='password123')
        course = Course.objects.create(title='Course', description='Test', difficulty='beginner')
        self.lesson = Lesson.objects.create(course=course, title='Unit 1', content='', order=1)
        self.client.force_authenticate(self.student)

    def test_activity_accumulates_seconds_without_rounding_each_ping(self):
        for seconds in (59, 2):
            response = self.client.post('/api/learning/activity/', {
                'lesson_id': self.lesson.id, 'seconds': seconds,
            }, format='json')
            self.assertEqual(response.status_code, 204)

        progress = LearningProgress.objects.get(student=self.student, lesson=self.lesson)
        self.assertEqual(progress.time_spent_seconds, 61)

    def test_activity_rejects_unreasonable_interval(self):
        response = self.client.post('/api/learning/activity/', {
            'lesson_id': self.lesson.id, 'seconds': 1801,
        }, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertFalse(LearningProgress.objects.exists())

    def test_activity_creates_immutable_detail_event(self):
        response = self.client.post('/api/learning/activity/', {
            'lesson_id': self.lesson.id, 'seconds': 12, 'page_url': '/lesson.html',
        }, format='json')
        self.assertEqual(response.status_code, 204)
        event = StudentEvent.objects.get()
        self.assertEqual(event.event_type, 'lesson_time')
        self.assertEqual(event.duration_ms, 12000)

    def test_client_events_are_idempotent_by_uuid(self):
        event_uuid = str(uuid.uuid4())
        payload = {'event_uuid': event_uuid, 'event_type': 'page_view', 'page_url': '/'}
        for _ in range(2):
            response = self.client.post('/api/learning/events/', payload, format='json')
            self.assertEqual(response.status_code, 201)
        self.assertEqual(StudentEvent.objects.filter(event_uuid=event_uuid).count(), 1)

    def test_client_events_store_client_time_tab_and_session(self):
        # 先心跳建立使用時段，事件應自動繫結
        self.client.post('/api/learning/heartbeat/')
        event_uuid = str(uuid.uuid4())
        payload = {
            'event_uuid': event_uuid, 'event_type': 'page_close', 'page_url': '/',
            'client_occurred_at': '2026-07-03T01:00:00Z',
            'tab_uuid': 'tab-1234',
        }
        response = self.client.post('/api/learning/events/', payload, format='json')
        self.assertEqual(response.status_code, 201)
        event = StudentEvent.objects.get(event_uuid=event_uuid)
        # USE_TZ=False：01:00 UTC 轉成本地（Asia/Taipei）naive 時間 09:00
        self.assertEqual(event.occurred_at.isoformat(), '2026-07-03T09:00:00')
        self.assertEqual(event.metadata.get('tab_uuid'), 'tab-1234')
        self.assertIsNotNone(event.session_id)

    def test_answer_change_event_keeps_full_answer_text(self):
        from apps.assessments.models import Quiz, Question, QuizAttempt
        from apps.learning.models import UnitRelease
        UnitRelease.objects.create(unit_number=1, is_open=True)
        quiz = Quiz.objects.create(lesson=self.lesson, title='Quiz')
        question = Question.objects.create(
            quiz=quiz, content='Q', question_type='short_answer', correct_answer='x', points=10,
        )
        attempt = QuizAttempt.objects.create(
            student=self.student, quiz=quiz, selected_question_ids=[question.id],
        )
        response = self.client.post('/api/assessments/interaction/', {
            'attempt_id': attempt.id, 'question_id': question.id,
            'event_type': 'answer_change', 'answer': 'draft answer B',
        }, format='json')
        self.assertEqual(response.status_code, 204)
        event = StudentEvent.objects.get(event_type='answer_change')
        self.assertEqual(event.metadata.get('answer'), 'draft answer B')
