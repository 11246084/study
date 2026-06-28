from rest_framework.test import APITestCase

from apps.courses.models import Course, Lesson
from apps.users.models import User
from .models import LearningProgress


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
        self.assertEqual(progress.time_spent, 1)

    def test_activity_rejects_unreasonable_interval(self):
        response = self.client.post('/api/learning/activity/', {
            'lesson_id': self.lesson.id, 'seconds': 1801,
        }, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertFalse(LearningProgress.objects.exists())
