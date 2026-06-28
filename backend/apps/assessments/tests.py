from django.utils import timezone
from rest_framework.test import APITestCase

from apps.courses.models import Course, Lesson
from apps.learning.models import AdaptiveLearningPath
from apps.users.models import User
from .models import Answer, Choice, Question, Quiz, QuizAttempt


class AssessmentSubmissionTests(APITestCase):
    def setUp(self):
        self.student = User.objects.create_user(username='student', password='password123')
        self.course = Course.objects.create(title='Course', description='Test', difficulty='beginner')
        self.lesson1 = Lesson.objects.create(course=self.course, title='Unit 1', content='', order=1)
        self.lesson2 = Lesson.objects.create(course=self.course, title='Unit 2', content='', order=2)
        self.quiz1 = Quiz.objects.create(lesson=self.lesson1, title='Quiz 1')
        self.quiz2 = Quiz.objects.create(lesson=self.lesson2, title='Quiz 2')
        self.question1 = Question.objects.create(
            quiz=self.quiz1, content='Q1', question_type='multiple_choice', points=40, order=1,
        )
        self.correct_choice = Choice.objects.create(
            question=self.question1, content='Correct', is_correct=True,
        )
        self.question2 = Question.objects.create(
            quiz=self.quiz1, content='Q2', question_type='short_answer',
            correct_answer='yes\n---OR---\ny', points=60, order=2,
        )
        self.foreign_question = Question.objects.create(
            quiz=self.quiz2, content='Foreign', question_type='short_answer',
            correct_answer='x', points=100, order=1,
        )
        self.client.force_authenticate(self.student)

    def payload(self, answers=None, quiz=None):
        return {
            'quiz_id': (quiz or self.quiz1).id,
            'answers': answers or [
                {'question_id': self.question1.id, 'student_answer': str(self.correct_choice.id)},
                {'question_id': self.question2.id, 'student_answer': 'y'},
            ],
        }

    def test_valid_answers_are_normalized_to_percentage(self):
        response = self.client.post('/api/assessments/submit/', self.payload(), format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['score'], 100.0)
        self.assertTrue(response.data['is_passed'])
        self.assertEqual(Answer.objects.count(), 2)

    def test_duplicate_question_is_rejected_without_partial_attempt(self):
        answers = [
            {'question_id': self.question1.id, 'student_answer': str(self.correct_choice.id)},
            {'question_id': self.question1.id, 'student_answer': str(self.correct_choice.id)},
        ]

        response = self.client.post('/api/assessments/submit/', self.payload(answers), format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(QuizAttempt.objects.count(), 0)

    def test_question_from_another_quiz_is_rejected(self):
        answers = [
            {'question_id': self.question1.id, 'student_answer': str(self.correct_choice.id)},
            {'question_id': self.foreign_question.id, 'student_answer': 'x'},
        ]

        response = self.client.post('/api/assessments/submit/', self.payload(answers), format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(QuizAttempt.objects.count(), 0)

    def test_locked_unit_is_enforced_by_api(self):
        response = self.client.get(f'/api/assessments/{self.quiz2.id}/')
        self.assertEqual(response.status_code, 403)

        QuizAttempt.objects.create(
            student=self.student, quiz=self.quiz1, completed_at=timezone.now(),
        )
        response = self.client.get(f'/api/assessments/{self.quiz2.id}/')
        self.assertEqual(response.status_code, 200)

    def test_coding_question_accepts_multiple_exact_answers(self):
        coding_quiz = Quiz.objects.create(lesson=self.lesson1, title='Coding')
        coding_question = Question.objects.create(
            quiz=coding_quiz,
            content='Write code',
            question_type='coding',
            correct_answer="print('ok')\n---OR---\nprint(\"ok\")",
            points=10,
        )
        payload = {
            'quiz_id': coding_quiz.id,
            'answers': [{'question_id': coding_question.id, 'student_answer': 'print("ok")'}],
        }

        response = self.client.post('/api/assessments/submit/', payload, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['score'], 100.0)
    def test_coding_question_ignores_spacing_and_case(self):
        coding_quiz = Quiz.objects.create(lesson=self.lesson1, title='Coding')
        coding_question = Question.objects.create(
            quiz=coding_quiz, content='Write code', question_type='coding',
            correct_answer="print('ok')", points=10,
        )
        payload = {
            'quiz_id': coding_quiz.id,
            'answers': [{'question_id': coding_question.id, 'student_answer': "PRINT( 'OK' )"}],
        }

        response = self.client.post('/api/assessments/submit/', payload, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['score'], 100.0)

    def test_coding_without_answer_is_rejected(self):
        coding_quiz = Quiz.objects.create(lesson=self.lesson1, title='Coding pending')
        coding_question = Question.objects.create(
            quiz=coding_quiz, content='Write code', question_type='coding', points=10,
        )
        payload = {
            'quiz_id': coding_quiz.id,
            'answers': [{'question_id': coding_question.id, 'student_answer': 'print(1)'}],
        }

        response = self.client.post('/api/assessments/submit/', payload, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(QuizAttempt.objects.count(), 0)
        self.assertFalse(AdaptiveLearningPath.objects.filter(student=self.student).exists())
