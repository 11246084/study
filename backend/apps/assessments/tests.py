from rest_framework.test import APITestCase

from apps.courses.models import Course, Lesson
from apps.learning.models import AdaptiveLearningPath, UnitRelease
from apps.users.models import User
from .models import Answer, Choice, Question, Quiz, QuizAttempt, QuestionInteraction


class AssessmentSubmissionTests(APITestCase):
    def setUp(self):
        self.student = User.objects.create_user(username='student', password='password123')
        self.course = Course.objects.create(title='Course', description='Test', difficulty='beginner')
        self.lesson1 = Lesson.objects.create(course=self.course, title='Unit 1', content='', order=1)
        self.lesson2 = Lesson.objects.create(course=self.course, title='Unit 2', content='', order=2)
        # 老師開放 Unit 1；Unit 2 保持鎖定（新解鎖規則：老師手動開放）
        UnitRelease.objects.create(unit_number=1, is_open=True)
        self.unit2_release = UnitRelease.objects.create(unit_number=2, is_open=False)
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
        quiz = quiz or self.quiz1
        selected_ids = [self.question1.id, self.question2.id]
        attempt = QuizAttempt.objects.create(
            student=self.student,
            quiz=quiz,
            pass_score_snapshot=quiz.pass_score,
            selected_question_ids=selected_ids,
        )
        return {
            'attempt_id': attempt.id,
            'quiz_id': quiz.id,
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

    def test_attempt_starts_before_submission_and_tracks_question(self):
        attempt = QuizAttempt.objects.create(
            student=self.student, quiz=self.quiz1,
            pass_score_snapshot=self.quiz1.pass_score,
            selected_question_ids=[self.question1.id, self.question2.id],
        )
        attempt_id = attempt.id
        interaction = self.client.post('/api/assessments/interaction/', {
            'attempt_id': attempt_id, 'question_id': self.question1.id,
            'event_type': 'answer_change', 'answer': str(self.correct_choice.id),
            'duration_ms': 2500,
        }, format='json')
        self.assertEqual(interaction.status_code, 204)
        payload = {
            'attempt_id': attempt_id,
            'quiz_id': self.quiz1.id,
            'answers': [
                {'question_id': self.question1.id, 'student_answer': str(self.correct_choice.id)},
                {'question_id': self.question2.id, 'student_answer': 'y'},
            ],
        }
        submitted = self.client.post('/api/assessments/submit/', payload, format='json')
        self.assertEqual(submitted.status_code, 201)
        self.assertEqual(QuizAttempt.objects.count(), 1)
        detail = QuestionInteraction.objects.get(attempt_id=attempt_id, question=self.question1)
        self.assertEqual(detail.answer_revision_count, 1)
        self.assertIsNotNone(detail.submitted_at)

    def test_duplicate_question_is_rejected_without_partial_attempt(self):
        answers = [
            {'question_id': self.question1.id, 'student_answer': str(self.correct_choice.id)},
            {'question_id': self.question1.id, 'student_answer': str(self.correct_choice.id)},
        ]

        response = self.client.post('/api/assessments/submit/', self.payload(answers), format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(QuizAttempt.objects.count(), 1)
        self.assertEqual(Answer.objects.count(), 0)

    def test_question_from_another_quiz_is_rejected(self):
        answers = [
            {'question_id': self.question1.id, 'student_answer': str(self.correct_choice.id)},
            {'question_id': self.foreign_question.id, 'student_answer': 'x'},
        ]

        response = self.client.post('/api/assessments/submit/', self.payload(answers), format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(QuizAttempt.objects.count(), 1)
        self.assertEqual(Answer.objects.count(), 0)

    def test_locked_unit_is_enforced_by_api(self):
        response = self.client.get(f'/api/assessments/{self.quiz2.id}/')
        self.assertEqual(response.status_code, 403)

        # 老師開放 Unit 2 後即可存取（不再依前一單元作答自動解鎖）
        self.unit2_release.is_open = True
        self.unit2_release.save()
        response = self.client.get(f'/api/assessments/{self.quiz2.id}/')
        self.assertEqual(response.status_code, 200)

    def test_submission_updates_level_for_unstarted_next_unit(self):
        response = self.client.post('/api/assessments/submit/', self.payload(), format='json')

        self.assertEqual(response.status_code, 201)
        path = AdaptiveLearningPath.objects.get(student=self.student, unit_number=2)
        self.assertEqual(path.current_level, 2)  # U1 Level 1 得 100 分，U2 升為 Level 2

    def test_retake_does_not_overwrite_started_next_unit_level(self):
        first = self.client.post('/api/assessments/submit/', self.payload(), format='json')
        self.assertEqual(first.status_code, 201)
        path = AdaptiveLearningPath.objects.get(student=self.student, unit_number=2)
        path.current_level = 3
        path.save(update_fields=['current_level'])
        QuizAttempt.objects.create(
            student=self.student, quiz=self.quiz2,
            selected_question_ids=[self.foreign_question.id],
        )

        retake = self.client.post('/api/assessments/submit/', self.payload(), format='json')

        self.assertEqual(retake.status_code, 201)
        path.refresh_from_db()
        self.assertEqual(path.current_level, 3)

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
            'attempt_id': QuizAttempt.objects.create(
                student=self.student, quiz=coding_quiz,
                selected_question_ids=[coding_question.id],
            ).id,
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
            'attempt_id': QuizAttempt.objects.create(
                student=self.student, quiz=coding_quiz,
                selected_question_ids=[coding_question.id],
            ).id,
            'quiz_id': coding_quiz.id,
            'answers': [{'question_id': coding_question.id, 'student_answer': "PRINT( 'OK' )"}],
        }

        response = self.client.post('/api/assessments/submit/', payload, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['score'], 100.0)

    def test_fill_blank_grades_each_blank_separately(self):
        fb_quiz = Quiz.objects.create(lesson=self.lesson1, title='Fill blank')
        fb_question = Question.objects.create(
            quiz=fb_quiz,
            content='輸出商與餘數。\n\n```python\ns = int(input())\nprint(s __1__ 60, s __2__ 60)\n```',
            question_type='fill_blank', correct_answer='//\n%', points=10,
        )
        attempt = QuizAttempt.objects.create(
            student=self.student, quiz=fb_quiz,
            selected_question_ids=[fb_question.id],
        )
        payload = {
            'attempt_id': attempt.id, 'quiz_id': fb_quiz.id,
            'answers': [{'question_id': fb_question.id, 'student_answer': ' // \n+'}],
        }

        response = self.client.post('/api/assessments/submit/', payload, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['score'], 50.0)  # 兩格對一格
        self.assertFalse(Answer.objects.get().is_correct)

    def test_fill_blank_accepts_alternatives_and_ignores_spacing(self):
        fb_quiz = Quiz.objects.create(lesson=self.lesson1, title='Fill blank alts')
        fb_question = Question.objects.create(
            quiz=fb_quiz,
            content='輸出 Amy 的分數。\n\n```python\nscores = {"Amy": 88}\nprint(scores[__1__])\n```',
            question_type='fill_blank', correct_answer='"Amy"|||\'Amy\'', points=10,
        )
        attempt = QuizAttempt.objects.create(
            student=self.student, quiz=fb_quiz,
            selected_question_ids=[fb_question.id],
        )
        payload = {
            'attempt_id': attempt.id, 'quiz_id': fb_quiz.id,
            'answers': [{'question_id': fb_question.id, 'student_answer': " 'Amy' "}],
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
            'attempt_id': QuizAttempt.objects.create(
                student=self.student, quiz=coding_quiz,
                selected_question_ids=[coding_question.id],
            ).id,
            'quiz_id': coding_quiz.id,
            'answers': [{'question_id': coding_question.id, 'student_answer': 'print(1)'}],
        }

        response = self.client.post('/api/assessments/submit/', payload, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(QuizAttempt.objects.count(), 1)
        self.assertEqual(Answer.objects.count(), 0)
        self.assertFalse(AdaptiveLearningPath.objects.filter(student=self.student).exists())

    def test_start_attempt_randomly_selects_ten_from_one_hundred(self):
        quiz = Quiz.objects.create(lesson=self.lesson1, title='Large bank')
        questions = [
            Question.objects.create(
                quiz=quiz, content=f'Bank question {index}',
                question_type='short_answer', correct_answer=str(index),
                points=1, order=index,
            )
            for index in range(1, 101)
        ]

        response = self.client.post('/api/assessments/start/', {'quiz_id': quiz.id}, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['quiz_data']['bank_size'], 100)
        self.assertEqual(response.data['quiz_data']['question_count'], 10)
        returned_ids = [item['id'] for item in response.data['quiz_data']['questions']]
        self.assertEqual(len(returned_ids), 10)
        self.assertEqual(len(set(returned_ids)), 10)
        self.assertTrue(set(returned_ids).issubset({question.id for question in questions}))
        attempt = QuizAttempt.objects.get(pk=response.data['id'])
        self.assertEqual(returned_ids, attempt.selected_question_ids)
        self.assertNotIn('correct_answer', response.data['quiz_data']['questions'][0])

    def test_start_attempt_does_not_repeat_a_tagged_pattern(self):
        quiz = Quiz.objects.create(lesson=self.lesson1, title='Tagged bank')
        for index in range(30):
            Question.objects.create(
                quiz=quiz, content=f'Question {index}', question_type='short_answer',
                correct_answer=str(index), points=1, order=index,
                concept=f'concept-{index % 5}', pattern=f'pattern-{index % 15}',
            )

        response = self.client.post('/api/assessments/start/', {'quiz_id': quiz.id}, format='json')

        self.assertEqual(response.status_code, 201)
        returned_ids = [item['id'] for item in response.data['quiz_data']['questions']]
        patterns = list(Question.objects.filter(id__in=returned_ids).values_list('pattern', flat=True))
        self.assertEqual(len(patterns), len(set(patterns)))

    def test_submit_rejects_question_not_selected_for_attempt(self):
        attempt = QuizAttempt.objects.create(
            student=self.student, quiz=self.quiz1,
            selected_question_ids=[self.question1.id],
        )
        response = self.client.post('/api/assessments/submit/', {
            'attempt_id': attempt.id,
            'quiz_id': self.quiz1.id,
            'answers': [
                {'question_id': self.question1.id, 'student_answer': str(self.correct_choice.id)},
                {'question_id': self.question2.id, 'student_answer': 'y'},
            ],
        }, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Answer.objects.count(), 0)

    def test_interaction_rejects_question_not_selected_for_attempt(self):
        attempt = QuizAttempt.objects.create(
            student=self.student, quiz=self.quiz1,
            selected_question_ids=[self.question1.id],
        )
        response = self.client.post('/api/assessments/interaction/', {
            'attempt_id': attempt.id,
            'question_id': self.question2.id,
            'event_type': 'question_view',
        }, format='json')

        self.assertEqual(response.status_code, 403)

    def test_quiz_summary_does_not_expose_question_bank(self):
        detail = self.client.get(f'/api/assessments/{self.quiz1.id}/')
        listing = self.client.get(f'/api/assessments/lesson/{self.lesson1.id}/')

        self.assertEqual(detail.status_code, 200)
        self.assertNotIn('questions', detail.data)
        self.assertEqual(listing.status_code, 200)
        self.assertNotIn('questions', listing.data['results'][0])
