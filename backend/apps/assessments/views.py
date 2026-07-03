import secrets

from django.utils import timezone
from django.db import transaction
from django.db.models import Exists, OuterRef
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, views, response, status
from rest_framework.exceptions import PermissionDenied, ValidationError
from .models import Quiz, QuizAttempt, Answer, Question, Choice, QuestionInteraction
from .serializers import (
    AttemptSubmitSerializer, QuestionSerializer, QuizAttemptSerializer,
    QuizSummarySerializer,
)
from apps.courses.models import Course, Lesson
from apps.courses.access import can_access_lesson

DIFFICULTY_TO_LEVEL = {'beginner': 1, 'intermediate': 2, 'advanced': 3}
LEVEL_TO_DIFFICULTY = {1: 'beginner', 2: 'intermediate', 3: 'advanced'}
LEVEL_NAMES = {1: 'Level 1 補救版', 2: 'Level 2 標準版', 3: 'Level 3 進階版'}
ANSWER_SEPARATOR = '\n---OR---\n'
BLANK_ALT_SEPARATOR = '|||'


def accepted_answers(raw_answer):
    """Return one or more accepted answers while preserving exact code spacing."""
    normalized = (raw_answer or '').replace('\r\n', '\n').replace('\r', '\n')
    if not normalized:
        return []
    return normalized.split(ANSWER_SEPARATOR)


def normalize_code_answer(value):
    """Ignore whitespace and letter case when comparing submitted code."""
    return ''.join((value or '').split()).casefold()


def normalize_blank_answer(value):
    """填空格比對：只忽略空白，保留大小寫（Python 區分大小寫）。"""
    return ''.join((value or '').split())


def fill_blank_config(raw_answer):
    """每行一格；同格多個可接受答案以 ||| 分隔。回傳 list[list[str]]。"""
    normalized = (raw_answer or '').replace('\r\n', '\n').replace('\r', '\n')
    blanks = []
    for line in normalized.split('\n'):
        if not line.strip():
            continue
        blanks.append([alt for alt in line.split(BLANK_ALT_SEPARATOR) if alt.strip()])
    return blanks


def grade_fill_blank(question, student_answer):
    """逐格批改，回傳 (答對格數, 總格數)。學生答案一行對應一格。"""
    blanks = fill_blank_config(question.correct_answer)
    submitted = (student_answer or '').replace('\r\n', '\n').replace('\r', '\n').split('\n')
    correct = 0
    for index, alternatives in enumerate(blanks):
        value = normalize_blank_answer(submitted[index]) if index < len(submitted) else ''
        if value and value in {normalize_blank_answer(alt) for alt in alternatives}:
            correct += 1
    return correct, len(blanks)


class QuizDetailView(generics.RetrieveAPIView):
    queryset = Quiz.objects.all()
    serializer_class = QuizSummarySerializer
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

        attempt_id = serializer.validated_data['attempt_id']
        attempt = get_object_or_404(
            QuizAttempt, pk=attempt_id, student=request.user, quiz=quiz,
        )
        if attempt.completed_at:
            raise ValidationError({'attempt_id': 'This attempt has already been submitted.'})
        selected_ids = [int(question_id) for question_id in attempt.selected_question_ids]
        if not selected_ids:
            raise ValidationError({'attempt_id': 'This attempt has no server-selected questions.'})

        submitted_answers = serializer.validated_data['answers']
        submitted_ids = [answer['question_id'] for answer in submitted_answers]
        if len(submitted_ids) != len(set(submitted_ids)):
            raise ValidationError({'answers': '每一題只能提交一次。'})

        if set(submitted_ids) != set(selected_ids):
            raise ValidationError({'answers': '答案必須完整且只能包含本次隨機抽出的題目。'})

        questions = {
            question.id: question
            for question in quiz.questions.filter(id__in=selected_ids)
        }
        if set(questions) != set(selected_ids):
            raise ValidationError({'attempt_id': '本次抽題內容已失效，請重新開始評量。'})

        total_score = 0
        maximum_score = sum(question.points for question in questions.values())
        missing_coding_answers = [
            question.id
            for question in questions.values()
            if question.question_type in {'coding', 'fill_blank'}
            and not question.correct_answer.strip()
        ]
        if missing_coding_answers:
            raise ValidationError({
                'quiz_id': '此評量尚有題目未設定標準答案，請通知教師補充後再作答。',
            })

        with transaction.atomic():
            attempt = get_object_or_404(
                QuizAttempt.objects.select_for_update(), pk=attempt_id,
                student=request.user, quiz=quiz,
            )
            if attempt.completed_at:
                raise ValidationError({'attempt_id': 'This attempt has already been submitted.'})
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
                elif question.question_type == 'fill_blank':
                    correct_blanks, total_blanks = grade_fill_blank(question, student_answer)
                    if total_blanks:
                        points_earned = round(question.points * correct_blanks / total_blanks, 4)
                        is_correct = correct_blanks == total_blanks

                Answer.objects.create(
                    attempt=attempt,
                    question=question,
                    student_answer=student_answer,
                    is_correct=is_correct,
                    points_earned=points_earned,
                )
                interaction, _ = QuestionInteraction.objects.get_or_create(
                    attempt=attempt, question=question,
                )
                interaction.final_answer = student_answer
                interaction.submitted_at = timezone.now()
                if not interaction.first_answered_at:
                    interaction.first_answered_at = interaction.submitted_at
                interaction.last_answered_at = interaction.submitted_at
                interaction.save()
                total_score += points_earned

            score_percent = round(total_score / maximum_score * 100, 2) if maximum_score else 0
            attempt.score = score_percent
            pass_score = attempt.pass_score_snapshot if attempt.pass_score_snapshot is not None else quiz.pass_score
            attempt.is_passed = score_percent >= pass_score
            attempt.completed_at = timezone.now()
            attempt.last_activity_at = attempt.completed_at
            attempt.save()

            from apps.learning.models import StudentEvent
            from apps.learning.tracking import event_context
            event_kwargs, meta_extra = event_context(request)
            StudentEvent.objects.create(
                student=request.user, event_type='quiz_submit', quiz=quiz,
                lesson=quiz.lesson, course=quiz.lesson.course,
                metadata={'attempt_id': attempt.id, 'score': score_percent,
                          'is_passed': attempt.is_passed, **meta_extra},
                **event_kwargs,
            )

            next_lesson_data = QuestionInteractionView()._run_adaptive_logic(
                request.user, quiz, score_percent,
            )

            # 更新給人看的彙總層（原始作答仍是真相來源，可整表重算）
            from apps.learning import summaries
            from apps.learning.models import AdaptiveLearningPath
            current_unit = quiz.lesson.order
            for unit in (current_unit, current_unit + 1):
                path_row = AdaptiveLearningPath.objects.filter(
                    student=request.user, unit_number=unit,
                ).first()
                if unit == current_unit:
                    level = path_row.current_level if path_row else DIFFICULTY_TO_LEVEL.get(
                        quiz.lesson.course.difficulty, 2)
                    summaries.record_attempt(request.user, unit, score_percent, level)
                elif path_row:
                    summaries.sync_level(request.user, unit, path_row.current_level)

        result = QuizAttemptSerializer(attempt).data
        result['next_lesson'] = next_lesson_data
        return response.Response(result, status=status.HTTP_201_CREATED)


class StartAttemptView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        quiz = get_object_or_404(
            Quiz.objects.select_related('lesson__course').prefetch_related('questions__choices'),
            pk=request.data.get('quiz_id'),
        )
        if not can_access_lesson(request, quiz.lesson):
            raise PermissionDenied('You cannot access this quiz.')
        question_bank = list(quiz.questions.all())
        if len(question_bank) < 10:
            raise ValidationError({'quiz_id': '題庫不足 10 題，請通知教師。'})
        if any(
            question.question_type in {'coding', 'fill_blank'} and not question.correct_answer.strip()
            for question in question_bank
        ):
            raise ValidationError({'quiz_id': '題庫尚有題目未設定標準答案。'})
        selected_questions = self._stratified_sample(question_bank, 10)
        selected_ids = [question.id for question in selected_questions]
        attempt = QuizAttempt.objects.create(
            student=request.user, quiz=quiz, pass_score_snapshot=quiz.pass_score,
            last_activity_at=timezone.now(),
            selected_question_ids=selected_ids,
        )
        from apps.learning.models import StudentEvent
        from apps.learning.tracking import event_context
        event_kwargs, meta_extra = event_context(request)
        StudentEvent.objects.create(
            student=request.user, event_type='quiz_open', quiz=quiz,
            lesson=quiz.lesson, course=quiz.lesson.course,
            metadata={'attempt_id': attempt.id, **meta_extra},
            **event_kwargs,
        )
        data = QuizAttemptSerializer(attempt).data
        quiz_data = QuizSummarySerializer(quiz).data
        quiz_data['question_count'] = len(selected_questions)
        quiz_data['questions'] = QuestionSerializer(selected_questions, many=True).data
        data['quiz_data'] = quiz_data
        return response.Response(data, status=status.HTTP_201_CREATED)

    @staticmethod
    def _stratified_sample(question_bank, count):
        """Choose broad concept coverage and never repeat a tagged pattern."""
        rng = secrets.SystemRandom()
        pool = list(question_bank)
        rng.shuffle(pool)
        selected = []
        used_patterns = set()
        concept_counts = {}

        while len(selected) < count:
            eligible = [
                question for question in pool
                if not question.pattern or question.pattern not in used_patterns
            ]
            if not eligible:
                break
            minimum = min(concept_counts.get(question.concept, 0) for question in eligible)
            balanced = [
                question for question in eligible
                if concept_counts.get(question.concept, 0) == minimum
            ]
            question = rng.choice(balanced)
            selected.append(question)
            pool.remove(question)
            if question.pattern:
                used_patterns.add(question.pattern)
            concept_counts[question.concept] = concept_counts.get(question.concept, 0) + 1

        # Untagged legacy rows may fill the remainder without weakening the
        # no-duplicate guarantee for rows that already have a pattern.
        if len(selected) < count:
            untagged = [question for question in pool if not question.pattern]
            needed = count - len(selected)
            if len(untagged) < needed:
                raise ValidationError({
                    'quiz_id': f'題庫只有 {len(used_patterns)} 種題型模式，無法抽出 {count} 題不重複試卷。'
                })
            selected.extend(rng.sample(untagged, needed))
        rng.shuffle(selected)
        return selected


class QuestionInteractionView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        attempt = get_object_or_404(
            QuizAttempt, pk=request.data.get('attempt_id'), student=request.user,
            completed_at__isnull=True,
        )
        question_id = request.data.get('question_id')
        if question_id not in attempt.selected_question_ids and str(question_id) not in {
            str(value) for value in attempt.selected_question_ids
        }:
            raise PermissionDenied('This question is not part of the current attempt.')
        question = get_object_or_404(Question, pk=question_id, quiz=attempt.quiz)
        event_type = request.data.get('event_type')
        if event_type not in {'question_view', 'answer_change'}:
            raise ValidationError({'event_type': 'Unsupported interaction event.'})
        try:
            duration_ms = max(0, min(int(request.data.get('duration_ms') or 0), 1800000))
        except (TypeError, ValueError):
            raise ValidationError({'duration_ms': 'Must be an integer.'})
        now = timezone.now()
        with transaction.atomic():
            interaction, _ = QuestionInteraction.objects.select_for_update().get_or_create(
                attempt=attempt, question=question,
            )
            if not interaction.first_viewed_at:
                interaction.first_viewed_at = now
            interaction.last_viewed_at = now
            interaction.duration_ms += duration_ms
            if event_type == 'answer_change':
                if not interaction.first_answered_at:
                    interaction.first_answered_at = now
                interaction.last_answered_at = now
                interaction.answer_revision_count += 1
                interaction.final_answer = str(request.data.get('answer') or '')
            interaction.save()
            attempt.last_activity_at = now
            attempt.save(update_fields=['last_activity_at'])
        from apps.learning.models import StudentEvent
        from apps.learning.tracking import event_context
        event_kwargs, meta_extra = event_context(request)
        metadata = {'attempt_id': attempt.id,
                    'revision': interaction.answer_revision_count, **meta_extra}
        # 保存當次答案全文，讓「空白→A→B→C」的修改歷程可完整重建
        if event_type == 'answer_change':
            metadata['answer'] = str(request.data.get('answer') or '')[:2000]
        StudentEvent.objects.create(
            student=request.user, event_type=event_type, quiz=attempt.quiz,
            lesson=attempt.quiz.lesson, course=attempt.quiz.lesson.course,
            question=question, duration_ms=duration_ms,
            metadata=metadata,
            **event_kwargs,
        )
        return response.Response(status=status.HTTP_204_NO_CONTENT)

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

        if score >= 80:
            if current_level < 3:
                rec_unit = current_unit
                rec_level = current_level + 1
                reason = f'Unit {current_unit} 得分 {score:.0f} 分（≥80），推薦挑戰 {LEVEL_NAMES[rec_level]}'
            elif next_unit <= 8:
                rec_unit = next_unit
                rec_level = next_level
                reason = f'Unit {current_unit} 得分 {score:.0f} 分（≥80），已是最高等級，繼續 Unit {next_unit} {LEVEL_NAMES[rec_level]}'
        elif score < 60:
            if current_level > 1:
                rec_unit = current_unit
                rec_level = current_level - 1
                reason = f'Unit {current_unit} 得分 {score:.0f} 分（<60），推薦先複習 {LEVEL_NAMES[rec_level]}'
            elif next_unit <= 8:
                rec_unit = next_unit
                rec_level = 1
                reason = f'Unit {current_unit} 得分 {score:.0f} 分（<60），繼續以 {LEVEL_NAMES[1]} 學習'
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
            QuizAttempt.objects.filter(student=student, completed_at__isnull=False)
            .values_list('quiz__lesson__order', flat=True)
        )
        if not all(u in attempted_units for u in range(1, 9)):
            return

        paths = list(AdaptiveLearningPath.objects.filter(student=student).order_by(
            'current_level', 'last_score', 'unit_number',
        )[:3])

        # 八單元完成後只保留這一輪總結推薦。API 以建立時間倒序顯示，
        # 因此反向建立，讓「等級最低、同級分數最低」出現在最前面。
        AdaptiveRecommendation.objects.filter(
            student=student, is_dismissed=False,
        ).update(is_dismissed=True)
        for path in reversed(paths):
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


class AbandonAttemptView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        attempt = get_object_or_404(
            QuizAttempt, pk=pk, student=request.user, completed_at__isnull=True,
        )
        if not attempt.abandoned_at:
            attempt.abandoned_at = timezone.now()
            attempt.last_activity_at = attempt.abandoned_at
            attempt.save(update_fields=['abandoned_at', 'last_activity_at'])
            from apps.learning.models import StudentEvent
            from apps.learning.tracking import event_context
            event_kwargs, meta_extra = event_context(request)
            StudentEvent.objects.create(
                student=request.user, event_type='quiz_abandon', quiz=attempt.quiz,
                lesson=attempt.quiz.lesson, course=attempt.quiz.lesson.course,
                metadata={'attempt_id': attempt.id, **meta_extra},
                **event_kwargs,
            )
        return response.Response(status=status.HTTP_204_NO_CONTENT)

class MyAttemptsView(generics.ListAPIView):
    serializer_class = QuizAttemptSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return QuizAttempt.objects.filter(student=self.request.user).order_by('-started_at')


class LessonQuizListView(generics.ListAPIView):
    """取得某單元的所有評量"""
    serializer_class = QuizSummarySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        lesson_id = self.kwargs['lesson_id']
        lesson = get_object_or_404(Lesson, pk=lesson_id)
        if not can_access_lesson(self.request, lesson):
            raise PermissionDenied('請先完成前一單元評量。')
        return Quiz.objects.filter(lesson=lesson).order_by('id')


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
            if a.question.question_type == 'fill_blank':
                parts = (a.student_answer or '').split('\n')
                return '；'.join(
                    f'空格{i}: {part.strip() or "（未填）"}' for i, part in enumerate(parts, start=1)
                )
            return a.student_answer

        def correct_answer_display(question):
            if question.question_type == 'multiple_choice':
                return question.choices.filter(is_correct=True).values_list('content', flat=True).first()
            if question.question_type == 'fill_blank':
                blanks = fill_blank_config(question.correct_answer)
                return '；'.join(
                    f'空格{i}: ' + ' 或 '.join(alt.strip() for alt in alternatives)
                    for i, alternatives in enumerate(blanks, start=1)
                )
            return question.correct_answer or None

        data['answers'] = [
            {
                'question_id': a.question.id,
                'question_type': a.question.question_type,
                'question_content': a.question.content,
                'explanation': a.question.explanation,
                'student_answer': student_answer_display(a),
                'is_correct': a.is_correct,
                'points_earned': a.points_earned,
                'correct_choice': correct_answer_display(a.question),
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
