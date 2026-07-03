from django.core.management.base import BaseCommand

from apps.assessments.models import Choice, Quiz

from .curriculum_questions import (
    CODING_QUESTIONS,
    QUIZ_QUESTIONS,
    SHORT_ANSWER_QUESTIONS,
)


class Command(BaseCommand):
    help = 'Synchronize existing formative quizzes with the generated question banks.'

    def handle(self, *args, **options):
        banks = {
            'beginner': (QUIZ_QUESTIONS, 'multiple_choice'),
            'intermediate': (SHORT_ANSWER_QUESTIONS, 'short_answer'),
            'advanced': (CODING_QUESTIONS, 'coding'),
        }
        updated = 0

        quizzes = Quiz.objects.filter(quiz_type='formative').select_related('lesson__course')
        for quiz in quizzes:
            bank_config = banks.get(quiz.lesson.course.difficulty)
            if not bank_config:
                continue

            bank, question_type = bank_config
            rows = bank[quiz.lesson.order - 1]
            questions = list(quiz.questions.order_by('order', 'id'))
            if len(questions) != len(rows):
                self.stdout.write(self.style.WARNING(
                    f'Skipped quiz {quiz.pk}: expected {len(rows)} questions, found {len(questions)}.'
                ))
                continue

            for order, (question, data) in enumerate(zip(questions, rows), start=1):
                question.content = data['content']
                question.question_type = question_type
                question.correct_answer = data.get('correct_answer', '')
                question.explanation = data.get('explanation', '')
                question.concept = data.get('concept', '')
                question.pattern = data.get('pattern', '')
                question.order = order
                question.save(update_fields=[
                    'content', 'question_type', 'correct_answer', 'explanation', 'concept', 'pattern', 'order',
                ])

                if question_type == 'multiple_choice':
                    question.choices.all().delete()
                    Choice.objects.bulk_create([
                        Choice(question=question, content=text, is_correct=is_correct)
                        for text, is_correct in data['choices']
                    ])
                updated += 1

        self.stdout.write(self.style.SUCCESS(f'Updated {updated} questions.'))
