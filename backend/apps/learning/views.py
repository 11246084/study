from django.db import transaction
from django.db.models import Exists, F, Max, OuterRef
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, permissions, views, response, status
from rest_framework.exceptions import PermissionDenied
from datetime import timedelta
import uuid
from .models import (LearningProgress, AdaptiveRecommendation,
                     AdaptiveLearningPath, StudySession, StudentEvent, UnitRelease)
from .serializers import LearningProgressSerializer, RecommendationSerializer
from . import summaries
from .tracking import event_context, parse_client_time
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


class RecommendationClickView(views.APIView):
    """學生點擊推薦卡時記錄點擊次數（RQ-04 推薦接受度埋點）"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        rec = get_object_or_404(AdaptiveRecommendation, pk=pk, student=request.user)
        rec.click_count += 1
        rec.last_clicked_at = timezone.now()
        rec.save(update_fields=['click_count', 'last_clicked_at'])
        event_kwargs, meta_extra = event_context(request)
        StudentEvent.objects.create(
            student=request.user, event_type='recommendation_click', recommendation=rec,
            lesson=rec.recommended_lesson, course=rec.recommended_lesson.course,
            metadata=meta_extra, **event_kwargs,
        )
        return response.Response({'id': rec.id, 'click_count': rec.click_count})


class RecommendationImpressionView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        rec = get_object_or_404(AdaptiveRecommendation, pk=pk, student=request.user)
        now = timezone.now()
        if not rec.first_impression_at:
            rec.first_impression_at = now
        rec.last_impression_at = now
        rec.impression_count += 1
        rec.save(update_fields=['first_impression_at', 'last_impression_at', 'impression_count'])
        event_kwargs, meta_extra = event_context(request)
        StudentEvent.objects.create(
            student=request.user, event_type='recommendation_impression', recommendation=rec,
            lesson=rec.recommended_lesson, course=rec.recommended_lesson.course,
            metadata=meta_extra, **event_kwargs,
        )
        return response.Response(status=status.HTTP_204_NO_CONTENT)


class RecommendationDismissView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        rec = get_object_or_404(AdaptiveRecommendation, pk=pk, student=request.user)
        rec.is_dismissed = True
        rec.dismissed_at = timezone.now()
        rec.save(update_fields=['is_dismissed', 'dismissed_at'])
        event_kwargs, meta_extra = event_context(request)
        StudentEvent.objects.create(
            student=request.user, event_type='recommendation_dismiss', recommendation=rec,
            lesson=rec.recommended_lesson, course=rec.recommended_lesson.course,
            metadata=meta_extra, **event_kwargs,
        )
        return response.Response(status=status.HTTP_204_NO_CONTENT)


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
            return response.Response({'detail': 'seconds 必須是整數。'}, status=status.HTTP_400_BAD_REQUEST)
        if seconds < 0 or seconds > 1800:
            return response.Response(
                {'detail': '單次活動時間必須介於 0 與 1800 秒。'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        lesson = get_object_or_404(Lesson, pk=lesson_id)

        with transaction.atomic():
            progress, _ = LearningProgress.objects.get_or_create(
                student=request.user, lesson=lesson,
            )
            progress = LearningProgress.objects.select_for_update().get(pk=progress.pk)
            # 載入即計一次瀏覽（seconds=0）；之後 ping 累計時數
            if seconds == 0:
                progress.visit_count += 1
            else:
                progress.time_spent_seconds += seconds
                summaries.record_lesson_time(request.user, lesson.order, seconds)
            if progress.status == 'not_started':
                progress.status = 'in_progress'
            progress.save()
            event_kwargs, meta_extra = event_context(request)
            StudentEvent.objects.create(
                student=request.user,
                event_type='lesson_open' if seconds == 0 else 'lesson_time',
                lesson=lesson, course=lesson.course, duration_ms=seconds * 1000,
                page_url=str(request.data.get('page_url') or '')[:1000],
                referrer=str(request.data.get('referrer') or '')[:1000],
                client_timezone=str(request.data.get('client_timezone') or '')[:50],
                app_version=str(request.data.get('app_version') or '')[:50],
                content_version=str(request.data.get('content_version') or '')[:50],
                metadata=meta_extra, **event_kwargs,
            )
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
            elapsed = max(0, min(int((now - latest.last_seen).total_seconds()), 120))
            latest.last_seen = now
            latest.active_seconds += elapsed
            latest.save(update_fields=['last_seen', 'active_seconds'])
        else:
            # 開新時段前，把逾時未關閉的舊時段補上明確的結束紀錄
            if latest and latest.ended_at is None:
                latest.ended_at = latest.last_seen
                latest.end_reason = 'timeout'
                latest.save(update_fields=['ended_at', 'end_reason'])
            latest = StudySession.objects.create(
                student=user, started_at=now, last_seen=now,
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
            )
            StudentEvent.objects.create(student=user, session=latest, event_type='session_start')
        return response.Response(status=status.HTTP_204_NO_CONTENT)


class EventBatchView(views.APIView):
    """Accept idempotent client events; duplicate UUIDs are ignored."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        items = request.data if isinstance(request.data, list) else [request.data]
        if len(items) > 100:
            return response.Response({'detail': 'At most 100 events per batch.'}, status=400)
        created = 0
        allowed = {'page_view', 'page_close', 'lesson_close', 'scroll_depth',
                   'video_play', 'video_pause', 'video_complete', 'download', 'client_error'}
        session = None
        for item in items:
            event_type = item.get('event_type')
            if event_type not in allowed:
                continue
            try:
                event_uuid = uuid.UUID(str(item.get('event_uuid')))
            except (ValueError, TypeError, AttributeError):
                continue
            if session is None:
                from .tracking import current_session
                session = current_session(request.user) or False
            metadata = item.get('metadata') if isinstance(item.get('metadata'), dict) else {}
            if item.get('tab_uuid'):
                metadata['tab_uuid'] = str(item['tab_uuid'])[:64]
            defaults = {
                'student': request.user,
                'event_type': event_type,
                'session': session or None,
                'page_url': str(item.get('page_url') or '')[:1000],
                'referrer': str(item.get('referrer') or '')[:1000],
                'duration_ms': max(0, min(int(item.get('duration_ms') or 0), 1800000)),
                'sequence_number': item.get('sequence_number'),
                'client_timezone': str(item.get('client_timezone') or '')[:50],
                'app_version': str(item.get('app_version') or '')[:50],
                'content_version': str(item.get('content_version') or '')[:50],
                'metadata': metadata,
            }
            occurred = parse_client_time(item.get('client_occurred_at'))
            if occurred:
                defaults['occurred_at'] = occurred
            if item.get('lesson_id'):
                defaults['lesson_id'] = item['lesson_id']
            try:
                _, was_created = StudentEvent.objects.get_or_create(
                    event_uuid=event_uuid, defaults=defaults,
                )
                created += int(was_created)
            except (ValueError, TypeError):
                continue
        return response.Response({'created': created}, status=status.HTTP_201_CREATED)


UNIT_TITLES = [
    '環境、變數、資料型態與 I/O',
    '條件判斷 If／Elif／Else',
    'For／While 與基礎演算法',
    '迴圈實作與基礎題庫',
    'List 與 String 進階操作',
    '串列與字串實戰題庫',
    '函式與模組化',
    '遞迴與 Dictionary 應用',
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
        # 老師手動開放的單元（取代舊的「前一單元有作答就解鎖」規則）
        open_units = set(
            UnitRelease.objects.filter(is_open=True).values_list('unit_number', flat=True)
        )
        # 取得已「提交」過評量的單元（不論是否通過）；未交卷中途離開不算完成
        attempted_units = set(
            QuizAttempt.objects.filter(student=student, completed_at__isnull=False)
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
                course_is_active = lesson.course.is_active
            except Lesson.DoesNotExist:
                lesson_id = None
                course_is_active = False

            # 單元由老師手動開放；未開放一律鎖定（已作答仍顯示完成）
            if not course_is_active and getattr(student, 'role', None) == 'student':
                status = 'course_closed'
            elif unit_num not in open_units:
                status = 'completed' if unit_num in attempted_units else 'locked'
            else:
                status = 'completed' if unit_num in attempted_units else 'available'

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
                'is_open': unit_num in open_units,
                'last_score': last_score if unit_num in attempted_units else None,
                'best_score': best_score_by_unit.get(unit_num),
            })

        return response.Response(result)


class UnitReleaseView(views.APIView):
    """老師／管理員控制單元開放。GET 列出 8 單元開關；POST 切換。"""
    permission_classes = [permissions.IsAuthenticated]

    def _check_management(self, request):
        if getattr(request, 'preview_as_admin', False):
            return
        if getattr(request.user, 'role', None) not in {'teacher', 'admin'} \
                and not request.user.is_staff and not request.user.is_superuser:
            raise PermissionDenied('僅限老師或管理員操作。')

    def get(self, request):
        self._check_management(request)
        releases = {r.unit_number: r for r in UnitRelease.objects.all()}
        return response.Response([
            {
                'unit_number': unit,
                'unit_title': UNIT_TITLES[unit - 1],
                'is_open': releases[unit].is_open if unit in releases else False,
                'opened_at': releases[unit].opened_at if unit in releases else None,
            }
            for unit in range(1, 9)
        ])

    def post(self, request):
        self._check_management(request)
        try:
            unit_number = int(request.data.get('unit_number'))
        except (TypeError, ValueError):
            return response.Response({'detail': 'unit_number 必須是 1~8 的整數。'}, status=400)
        if not 1 <= unit_number <= 8:
            return response.Response({'detail': 'unit_number 必須是 1~8 的整數。'}, status=400)
        is_open = bool(request.data.get('is_open'))
        release, _ = UnitRelease.objects.get_or_create(unit_number=unit_number)
        release.is_open = is_open
        release.opened_at = timezone.now() if is_open else release.opened_at
        release.opened_by = request.user
        release.save()
        return response.Response({'unit_number': unit_number, 'is_open': release.is_open})
