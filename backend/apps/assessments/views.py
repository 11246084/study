from django.utils import timezone
from rest_framework import generics, permissions, views, response, status
from .models import Quiz, QuizAttempt, Answer, Question, Choice
from .serializers import QuizSerializer, AttemptSubmitSerializer, QuizAttemptSerializer
from apps.courses.models import Course, Lesson

DIFFICULTY_TO_LEVEL = {'beginner': 1, 'intermediate': 2, 'advanced': 3}
LEVEL_TO_DIFFICULTY = {1: 'beginner', 2: 'intermediate', 3: 'advanced'}
LEVEL_NAMES = {1: 'Level 1 補救版', 2: 'Level 2 標準版', 3: 'Level 3 進階版'}


class QuizDetailView(generics.RetrieveAPIView):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = [permissions.IsAuthenticated]


class SubmitAttemptView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = AttemptSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        quiz = Quiz.objects.get(pk=serializer.validated_data['quiz_id'])
        attempt = QuizAttempt.objects.create(student=request.user, quiz=quiz)

        total_score = 0
        for ans_data in serializer.validated_data['answers']:
            question = Question.objects.get(pk=ans_data['question_id'])
            is_correct = False
            points_earned = 0

            if question.question_type == 'multiple_choice':
                correct = question.choices.filter(is_correct=True).first()
                if correct and str(correct.id) == ans_data['student_answer']:
                    is_correct = True
                    points_earned = question.points
            elif question.question_type == 'short_answer':
                student_ans = ans_data['student_answer'].strip().lower()
                correct_ans = question.correct_answer.strip().lower()
                if student_ans and student_ans == correct_ans:
                    is_correct = True
                    points_earned = question.points
            elif question.question_type == 'coding':
                if ans_data['student_answer'].strip():
                    is_correct = True
                    points_earned = question.points

            Answer.objects.create(
                attempt=attempt,
                question=question,
                student_answer=ans_data['student_answer'],
                is_correct=is_correct,
                points_earned=points_earned,
            )
            total_score += points_earned

        attempt.score = total_score
        attempt.is_passed = total_score >= quiz.pass_score
        attempt.completed_at = timezone.now()
        attempt.save()

        next_lesson_data = self._run_adaptive_logic(request.user, quiz, total_score)

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
                    recommended_lesson__order=rec_unit,
                ).update(is_dismissed=True)

                AdaptiveRecommendation.objects.create(
                    student=student,
                    recommended_lesson=rec_lesson,
                    reason=reason,
                )

                next_lesson_data = {
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
        return Quiz.objects.filter(lesson_id=lesson_id)


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
        rec = AdaptiveRecommendation.objects.filter(
            student=request.user,
            is_dismissed=False,
        ).order_by('-created_at').first()

        if rec:
            rec_level = DIFFICULTY_TO_LEVEL.get(rec.recommended_lesson.course.difficulty, 2)
            data['next_lesson'] = {
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
