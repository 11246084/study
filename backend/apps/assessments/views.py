from django.utils import timezone
from django.db import transaction
from django.db.models import Exists, OuterRef
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, views, response, status
from rest_framework.exceptions import PermissionDenied, ValidationError
from .models import Quiz, QuizAttempt, Answer, Question, Choice
from .serializers import QuizSerializer, AttemptSubmitSerializer, QuizAttemptSerializer
from apps.courses.models import Course, Lesson
from apps.courses.access import can_access_lesson

DIFFICULTY_TO_LEVEL = {'beginner': 1, 'intermediate': 2, 'advanced': 3}
LEVEL_TO_DIFFICULTY = {1: 'beginner', 2: 'intermediate', 3: 'advanced'}
LEVEL_NAMES = {1: 'Level 1 補救版', 2: 'Level 2 標準版', 3: 'Level 3 進階版'}
ANSWER_SEPARATOR = '\n---OR---\n'


def accepted_answers(raw_answer):
    """Return one or more accepted answers while preserving exact code spacing."""
    normalized = (raw_answer or '').replace('\r\n', '\n').replace('\r', '\n')
    if not normalized:
        return []
    return normalized.split(ANSWER_SEPARATOR)


def normalize_code_answer(value):
    """Ignore whitespace and letter case when comparing submitted code."""
    return ''.join((value or '').split()).casefold()


class QuizDetailView(generics.RetrieveAPIView):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        quiz = super().get_object()
        if not can_access_lesson(self.request, quiz.lesson):
            raise PermissionDenied('請先完成前一單元評量。')
        return quiz


class SubmitAttemptView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = AttemptSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        quiz = get_object_or_404(
            Quiz.objects.prefetch_related('questions__choices').select_related('lesson'),
            pk=serializer.validated_data['quiz_id'],
        )
        if not can_access_lesson(request, quiz.lesson):
            raise PermissionDenied('請先完成前一單元評量。')

        submitted_answers = serializer.validated_data['answers']
        submitted_ids = [answer['question_id'] for answer in submitted_answers]
        if len(submitted_ids) != len(set(submitted_ids)):
            raise ValidationError({'answers': '每一題只能提交一次。'})

        questions = {question.id: question for question in quiz.questions.all()}
        if set(submitted_ids) != set(questions):
            raise ValidationError({'answers': '答案必須完整且只能包含此評量的題目。'})

        total_score = 0
        maximum_score = sum(question.points for question in questions.values())
        missing_coding_answers = [
            question.id
            for question in questions.values()
            if question.question_type == 'coding' and not accepted_answers(question.correct_answer)
        ]
        if missing_coding_answers:
            raise ValidationError({
                'quiz_id': '此評量尚有程式題未設定標準答案，請通知教師補充後再作答。',
            })

        with transaction.atomic():
            attempt = QuizAttempt.objects.create(student=request.user, quiz=quiz)
            for ans_data in submitted_answers:
                question = questions[ans_data['question_id']]
                student_answer = ans_data['student_answer']
                is_correct = False
                points_earned = 0

                if question.question_type == 'multiple_choice':
                    correct = question.choices.filter(is_correct=True).first()
                    if correct and str(correct.id) == student_answer:
                        is_correct = True
                        points_earned = question.points
                elif question.question_type in {'short_answer', 'true_false'}:
                    normalized_answer = student_answer.strip().casefold()
                    possible_answers = {
                        answer.strip().casefold()
                        for answer in accepted_answers(question.correct_answer)
                        if answer.strip()
                    }
                    if normalized_answer and normalized_answer in possible_answers:
                        is_correct = True
                        points_earned = question.points
                elif question.question_type == 'coding':
                    normalized_code = normalize_code_answer(student_answer)
                    possible_answers = {
                        normalize_code_answer(answer)
                        for answer in accepted_answers(question.correct_answer)
                    }
                    if normalized_code in possible_answers:
                        is_correct = True
                        points_earned = question.points

                Answer.objects.create(
                    attempt=attempt,
                    question=question,
                    student_answer=student_answer,
                    is_correct=is_correct,
                    points_earned=points_earned,
                )
                total_score += points_earned

            score_percent = round(total_score / maximum_score * 100, 2) if maximum_score else 0
            attempt.score = score_percent
            attempt.is_passed = score_percent >= quiz.pass_score
            attempt.completed_at = timezone.now()
            attempt.save()

            next_lesson_data = self._run_adaptive_logic(request.user, quiz, score_percent)

        result = QuizAttemptSerializer(attempt).data
        result['next_lesson'] = next_lesson_data
        return response.Response(result, status=status.HTTP_201_CREATED)

    def _run_adaptive_logic(self, student, quiz, score):
        """
        雙軌適性邏輯：
          垂直路徑 — 更新 next_unit 的 AdaptiveLearningPath 等級
          水平路徑 — 建立 AdaptiveRecommendation（同單元換等級 or 下一單元）
        """
        from apps.learning.models import AdaptiveLearningPath, AdaptiveRecommendation

        current_lesson = quiz.lesson
        current_unit = current_lesson.order
        current_level = DIFFICULTY_TO_LEVEL.get(current_lesson.course.difficulty, 2)

        # 更新當前單元的學習路徑
        path, _ = AdaptiveLearningPath.objects.get_or_create(
            student=student,
            unit_number=current_unit,
            defaults={'current_level': current_level},
        )
        path.last_score = score
        path.current_level = current_level
        path.save()

        # ── 垂直路徑：更新下一單元等級 ──────────────────────────────
        next_unit = current_unit + 1
        next_level = AdaptiveLearningPath.determine_next_level(current_level, score)
        if next_unit <= 8:
            next_path, _ = AdaptiveLearningPath.objects.get_or_create(
                student=student,
                unit_number=next_unit,
                defaults={'current_level': next_level},
            )
            next_path.current_level = next_level
            next_path.save()

        # ── 水平路徑：決定推薦目標 ───────────────────────────────────
        rec_unit = None
        rec_level = None
        reason = ''

        if score >= 90:
            if current_level < 3:
                rec_unit = current_unit
                rec_level = current_level + 1
                reason = f'Unit {current_unit} 得分 {score:.0f} 分（≥90），推薦挑戰 {LEVEL_NAMES[rec_level]}'
            elif next_unit <= 8:
                rec_unit = next_unit
                rec_level = next_level
                reason = f'Unit {current_unit} 得分 {score:.0f} 分（≥90），已是最高等級，繼續 Unit {next_unit} {LEVEL_NAMES[rec_level]}'
        elif score < 80:
            if current_level > 1:
                rec_unit = current_unit
                rec_level = current_level - 1
                reason = f'Unit {current_unit} 得分 {score:.0f} 分（<80），推薦先複習 {LEVEL_NAMES[rec_level]}'
            elif next_unit <= 8:
                rec_unit = next_unit
                rec_level = 1
                reason = f'Unit {current_unit} 得分 {score:.0f} 分（<80），繼續以 {LEVEL_NAMES[1]} 學習'
        else:
            if next_unit <= 8:
                rec_unit = next_unit
                rec_level = next_level
                reason = f'Unit {current_unit} 得分 {score:.0f} 分，繼續以 {LEVEL_NAMES[rec_level]} 學習'

        # ── 建立推薦記錄 ─────────────────────────────────────────────
        next_lesson_data = None
        if rec_unit and rec_level:
            try:
                rec_lesson = Lesson.objects.get(
                    course__difficulty=LEVEL_TO_DIFFICULTY[rec_level],
                    order=rec_unit,
                )
            except Lesson.DoesNotExist:
                rec_lesson = None

            if rec_lesson:
                # 若推薦的是同一單元不同等級，同步更新該單元的 current_level
                if rec_unit == current_unit:
                    path.current_level = rec_level
                    path.save()

                AdaptiveRecommendation.objects.filter(
                    student=student,
                    recommended_lesson__order__in=[rec_unit, current_unit],
                ).update(is_dismissed=True)

                created_rec = AdaptiveRecommendation.objects.create(
                    student=student,
                    recommended_lesson=rec_lesson,
                    reason=reason,
                )

                next_lesson_data = {
                    'recommendation_id': created_rec.id,
                    'lesson_id': rec_lesson.id,
                    'lesson_title': rec_lesson.title,
                    'unit_number': rec_unit,
                    'is_same_unit': rec_unit == current_unit,
                    'level': rec_level,
                    'level_name': LEVEL_NAMES[rec_level],
                    'reason': reason,
                }

        # ── 全部 8 單元完成 → 推薦最弱的 3 個單元 ────────────────────
        if current_unit == 8:
            self._recommend_weakest_units(student)

        return next_lesson_data

    def _recommend_weakest_units(self, student):
        from apps.learning.models import AdaptiveLearningPath, AdaptiveRecommendation

        attempted_units = set(
            QuizAttempt.objects.filter(student=student)
            .values_list('quiz__lesson__order', flat=True)
        )
        if not all(u in attempted_units for u in range(1, 9)):
            return

        paths = AdaptiveLearningPath.objects.filter(student=student).order_by('last_score')[:3]
        for path in paths:
            try:
                lesson = Lesson.objects.get(
                    course__difficulty=LEVEL_TO_DIFFICULTY[path.current_level],
                    order=path.unit_number,
                )
            except Lesson.DoesNotExist:
                continue
            AdaptiveRecommendation.objects.create(
                student=student,
                recommended_lesson=lesson,
                reason=f'Unit {path.unit_number} 得分 {path.last_score:.0f} 分，建議複習加強 {LEVEL_NAMES[path.current_level]}',
            )


class MyAttemptsView(generics.ListAPIView):
    serializer_class = QuizAttemptSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return QuizAttempt.objects.filter(student=self.request.user).order_by('-started_at')


class LessonQuizListView(generics.ListAPIView):
    """取得某單元的所有評量"""
    serializer_class = QuizSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        lesson_id = self.kwargs['lesson_id']
        lesson = get_object_or_404(Lesson, pk=lesson_id)
        if not can_access_lesson(self.request, lesson):
            raise PermissionDenied('請先完成前一單元評量。')
        return Quiz.objects.filter(lesson=lesson)


class AttemptDetailView(generics.RetrieveAPIView):
    """取得單筆作答記錄（含答案詳情與最新適性推薦）"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        from .models import Answer
        from apps.learning.models import AdaptiveRecommendation
        try:
            attempt = QuizAttempt.objects.get(pk=pk, student=request.user)
        except QuizAttempt.DoesNotExist:
            return response.Response({'detail': '找不到作答記錄'}, status=status.HTTP_404_NOT_FOUND)

        data = QuizAttemptSerializer(attempt).data
        answers = Answer.objects.filter(attempt=attempt).select_related('question')
        def student_answer_display(a):
            if a.question.question_type == 'multiple_choice':
                try:
                    return Choice.objects.get(id=int(a.student_answer)).content
                except (Choice.DoesNotExist, ValueError):
                    return a.student_answer
            return a.student_answer

        data['answers'] = [
            {
                'question_id': a.question.id,
                'question_type': a.question.question_type,
                'question_content': a.question.content,
                'explanation': a.question.explanation,
                'student_answer': student_answer_display(a),
                'is_correct': a.is_correct,
                'points_earned': a.points_earned,
                'correct_choice': (
                    a.question.choices.filter(is_correct=True).values_list('content', flat=True).first()
                    if a.question.question_type == 'multiple_choice'
                    else a.question.correct_answer or None
                ),
            }
            for a in answers
        ]

        # 附上最新的適性推薦（建立時間 >= 本次作答完成時間）
        current_unit = attempt.quiz.lesson.order
        later_attempt_for_recommended_unit = QuizAttempt.objects.filter(
            student=request.user,
            quiz__lesson__order=OuterRef('recommended_lesson__order'),
            completed_at__gt=OuterRef('created_at'),
        )
        later_unit_attempt = QuizAttempt.objects.filter(
            student=request.user,
            quiz__lesson__order__gt=OuterRef('recommended_lesson__order'),
            completed_at__gt=OuterRef('created_at'),
        )
        rec = (
            AdaptiveRecommendation.objects.filter(
                student=request.user,
                is_dismissed=False,
            )
            .annotate(
                is_stale=Exists(later_attempt_for_recommended_unit),
                is_from_previous_unit=Exists(later_unit_attempt),
            )
            .filter(is_stale=False, is_from_previous_unit=False)
            .order_by('-created_at')
            .first()
        )

        if rec:
            rec_level = DIFFICULTY_TO_LEVEL.get(rec.recommended_lesson.course.difficulty, 2)
            data['next_lesson'] = {
                'recommendation_id': rec.id,
                'lesson_id': rec.recommended_lesson.id,
                'lesson_title': rec.recommended_lesson.title,
                'unit_number': rec.recommended_lesson.order,
                'is_same_unit': rec.recommended_lesson.order == current_unit,
                'level': rec_level,
                'level_name': LEVEL_NAMES[rec_level],
                'reason': rec.reason,
            }
        else:
            data['next_lesson'] = None

        return response.Response(data)
