from django.db.models import Exists, F, Max, OuterRef
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, permissions, views, response, status
from datetime import timedelta
from .models import LearningProgress, AdaptiveRecommendation, PerformanceRecord, AdaptiveLearningPath, StudySession
from .serializers import LearningProgressSerializer, RecommendationSerializer, PerformanceSerializer
from apps.courses.models import Lesson
from apps.assessments.models import QuizAttempt


class LearningProgressView(generics.ListCreateAPIView):
    serializer_class = LearningProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return LearningProgress.objects.filter(student=self.request.user)

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)


class ProgressUpdateView(generics.UpdateAPIView):
    serializer_class = LearningProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return LearningProgress.objects.filter(student=self.request.user)


class RecommendationListView(generics.ListAPIView):
    serializer_class = RecommendationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        student = self.request.user

        later_attempt_for_recommended_unit = QuizAttempt.objects.filter(
            student=student,
            quiz__lesson__order=OuterRef('recommended_lesson__order'),
            completed_at__gt=OuterRef('created_at'),
        )
        later_unit_attempt = QuizAttempt.objects.filter(
            student=student,
            quiz__lesson__order__gt=OuterRef('recommended_lesson__order'),
            completed_at__gt=OuterRef('created_at'),
        )

        return (
            AdaptiveRecommendation.objects.filter(student=student, is_dismissed=False)
            .annotate(
                is_stale=Exists(later_attempt_for_recommended_unit),
                is_from_previous_unit=Exists(later_unit_attempt),
            )
            .filter(is_stale=False)
            .filter(is_from_previous_unit=False)
            .select_related('recommended_lesson', 'recommended_lesson__course')
            .order_by('-created_at')
        )


class PerformanceListView(generics.ListAPIView):
    serializer_class = PerformanceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PerformanceRecord.objects.filter(student=self.request.user)


class RecommendationClickView(views.APIView):
    """學生點擊推薦卡時記錄 is_clicked / clicked_at（RQ-04 推薦接受度埋點）"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        rec = get_object_or_404(AdaptiveRecommendation, pk=pk, student=request.user)
        if not rec.is_clicked:
            rec.is_clicked = True
            rec.clicked_at = timezone.now()
            rec.save(update_fields=['is_clicked', 'clicked_at'])
        return response.Response({'id': rec.id, 'is_clicked': rec.is_clicked})


class ActivityPingView(views.APIView):
    """記錄教材瀏覽次數與線上時數（RQ-05 投入度代理變數埋點）

    body: { "lesson_id": <int>, "seconds": <int> }
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        lesson_id = request.data.get('lesson_id')
        try:
            seconds = int(request.data.get('seconds') or 0)
        except (TypeError, ValueError):
            seconds = 0
        lesson = get_object_or_404(Lesson, pk=lesson_id)

        progress, created = LearningProgress.objects.get_or_create(
            student=request.user, lesson=lesson,
        )
        # 載入即計一次瀏覽（seconds=0）；之後 ping 累計時數
        if seconds <= 0:
            progress.visit_count = F('visit_count') + 1
        else:
            progress.time_spent = F('time_spent') + seconds // 60
        if progress.status == 'not_started':
            progress.status = 'in_progress'
        progress.save()
        return response.Response(status=status.HTTP_204_NO_CONTENT)


class SessionHeartbeatView(views.APIView):
    """記錄使用時段（RQ-05 使用時間/次數）。前端登入後定期 POST。

    距上次活動超過 GAP_MINUTES 視為新時段，否則延長現有時段。
    僅對學生帳號計入，避免老師/管理員預覽汙染研究資料。
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        if getattr(user, 'role', None) != 'student':
            return response.Response(status=status.HTTP_204_NO_CONTENT)
        now = timezone.now()
        gap = timedelta(minutes=StudySession.GAP_MINUTES)
        latest = StudySession.objects.filter(student=user).order_by('-last_seen').first()
        if latest and (now - latest.last_seen) <= gap:
            latest.last_seen = now
            latest.save(update_fields=['last_seen'])
        else:
            StudySession.objects.create(student=user, started_at=now, last_seen=now)
        return response.Response(status=status.HTTP_204_NO_CONTENT)


UNIT_TITLES = [
    'print 輸出',
    'input 輸入與運算',
    'if 條件判斷',
    '多條件 if',
    'list 串列',
    'range 數列',
    'for 迴圈',
    '迴圈應用',
]

LEVEL_TO_DIFFICULTY = {1: 'beginner', 2: 'intermediate', 3: 'advanced'}
LEVEL_NAMES = {1: 'Level 1 補救版', 2: 'Level 2 標準版', 3: 'Level 3 進階版'}


class AdaptivePathView(views.APIView):
    """回傳學生的 8 個單元學習路徑（含當前等級、課程連結、完成狀態）"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        student = request.user
        path_records = {
            p.unit_number: p
            for p in AdaptiveLearningPath.objects.filter(student=student)
        }
        # 取得已作答過評量的單元（不論是否通過）
        attempted_units = set(
            QuizAttempt.objects.filter(student=student)
            .values_list('quiz__lesson__order', flat=True)
        )
        best_score_by_unit = {
            row['unit']: row['best_score']
            for row in QuizAttempt.objects.filter(student=student, completed_at__isnull=False)
            .values(unit=F('quiz__lesson__order'))
            .annotate(best_score=Max('score'))
        }
        # 取得通過評量的單元（用於顯示狀態）
        passed_units = set(
            QuizAttempt.objects.filter(student=student, is_passed=True)
            .values_list('quiz__lesson__order', flat=True)
        )

        result = []
        for unit_num in range(1, 9):
            path = path_records.get(unit_num)
            level = path.current_level if path else 2  # 預設 Level 2
            last_score = path.last_score if path else None

            difficulty = LEVEL_TO_DIFFICULTY[level]
            try:
                lesson = Lesson.objects.get(course__difficulty=difficulty, order=unit_num)
                lesson_id = lesson.id
            except Lesson.DoesNotExist:
                lesson_id = None

            # 第 1 單元永遠可學；之後只要前一單元有作答評量就解鎖
            if unit_num == 1:
                status = 'completed' if unit_num in attempted_units else 'available'
            else:
                prev_attempted = (unit_num - 1) in attempted_units
                if unit_num in attempted_units:
                    status = 'completed'
                elif prev_attempted:
                    status = 'available'
                else:
                    status = 'locked'

            # 三個等級的 lesson_id，供前端等級切換使用
            all_levels = {}
            for lvl_num, lvl_diff in LEVEL_TO_DIFFICULTY.items():
                try:
                    lvl_lesson = Lesson.objects.get(course__difficulty=lvl_diff, order=unit_num)
                    all_levels[lvl_num] = lvl_lesson.id
                except Lesson.DoesNotExist:
                    all_levels[lvl_num] = None

            result.append({
                'unit_number': unit_num,
                'unit_title': UNIT_TITLES[unit_num - 1],
                'current_level': level,
                'level_name': LEVEL_NAMES[level],
                'lesson_id': lesson_id,
                'all_levels': all_levels,
                'status': status,
                'last_score': last_score if unit_num in attempted_units else None,
                'best_score': best_score_by_unit.get(unit_num),
            })

        return response.Response(result)
