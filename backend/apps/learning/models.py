from django.db import models
from django.utils import timezone
import uuid
from apps.users.models import User
from apps.courses.models import Course, Lesson


class LearningProgress(models.Model):
    STATUS_CHOICES = [
        ('not_started', '未開始'),
        ('in_progress', '學習中'),
        ('completed', '已完成'),
    ]
    student = models.ForeignKey(User, on_delete=models.PROTECT, related_name='progress', verbose_name='學生')
    lesson = models.ForeignKey(Lesson, on_delete=models.PROTECT, related_name='progress', verbose_name='單元')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started', verbose_name='狀態')
    time_spent_seconds = models.PositiveIntegerField(default=0, verbose_name='花費時間(秒)')
    visit_count = models.PositiveIntegerField(default=0, verbose_name='瀏覽次數')
    last_accessed = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = '學習進度'
        verbose_name_plural = '學習進度'
        unique_together = ('student', 'lesson')

    def __str__(self):
        return f'{self.student.username} - {self.lesson.title} ({self.get_status_display()})'


class AdaptiveRecommendation(models.Model):
    student = models.ForeignKey(User, on_delete=models.PROTECT, related_name='recommendations', verbose_name='學生')
    recommended_lesson = models.ForeignKey(Lesson, on_delete=models.PROTECT, verbose_name='推薦單元')
    reason = models.CharField(max_length=500, verbose_name='推薦原因')
    created_at = models.DateTimeField(auto_now_add=True)
    is_dismissed = models.BooleanField(default=False, verbose_name='是否忽略')
    impression_count = models.PositiveIntegerField(default=0, verbose_name='曝光次數')
    first_impression_at = models.DateTimeField(null=True, blank=True)
    last_impression_at = models.DateTimeField(null=True, blank=True)
    click_count = models.PositiveIntegerField(default=0, verbose_name='點擊次數')
    last_clicked_at = models.DateTimeField(null=True, blank=True)
    dismissed_at = models.DateTimeField(null=True, blank=True)
    algorithm_version = models.CharField(max_length=50, default='adaptive-v1')

    class Meta:
        verbose_name = '適性推薦'
        verbose_name_plural = '適性推薦'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.student.username} → {self.recommended_lesson.title}'


class AdaptiveLearningPath(models.Model):
    """
    記錄每位學生在每個「單元編號」上的當前等級。
    unit_number: 1~8（對應 8 個教學單元）
    current_level: 1=補救, 2=標準, 3=進階
    分流規則：score >= 80 → 升階；score < 60 → 降階；60~79 → 維持
    """
    LEVEL_CHOICES = [
        (1, 'Level 1 補救版'),
        (2, 'Level 2 標準版'),
        (3, 'Level 3 進階版'),
    ]
    student = models.ForeignKey(User, on_delete=models.PROTECT, related_name='adaptive_path', verbose_name='學生')
    unit_number = models.PositiveIntegerField(verbose_name='單元編號')
    current_level = models.IntegerField(choices=LEVEL_CHOICES, default=2, verbose_name='當前等級')
    last_score = models.FloatField(default=0.0, verbose_name='最近評量分數')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '適性學習路徑'
        verbose_name_plural = '適性學習路徑'
        unique_together = ('student', 'unit_number')
        ordering = ['unit_number']
        constraints = [
            models.CheckConstraint(
                condition=models.Q(unit_number__gte=1, unit_number__lte=8),
                name='adaptive_unit_between_1_and_8',
            ),
            models.CheckConstraint(
                condition=models.Q(current_level__gte=1, current_level__lte=3),
                name='adaptive_level_between_1_and_3',
            ),
            models.CheckConstraint(
                condition=models.Q(last_score__gte=0, last_score__lte=100),
                name='adaptive_score_between_0_and_100',
            ),
        ]

    def __str__(self):
        return f'{self.student.username} Unit{self.unit_number} Lv{self.current_level}'

    @staticmethod
    def determine_next_level(current_level: int, score: float) -> int:
        """依分數決定下一單元的等級"""
        if score >= 80 and current_level < 3:
            return current_level + 1
        if score < 60 and current_level > 1:
            return current_level - 1
        return current_level


class StudySession(models.Model):
    """一段連續使用系統的時段（RQ-05 使用時間/次數）。

    前端定期送 heartbeat；若距上次心跳超過 GAP_MINUTES 視為新的一段，
    否則延長現有時段的 last_seen。用於計算每週使用次數、每週時長、每次使用長度。
    """
    GAP_MINUTES = 30

    student = models.ForeignKey(User, on_delete=models.PROTECT, related_name='study_sessions', verbose_name='學生')
    started_at = models.DateTimeField(default=timezone.now, verbose_name='開始時間')
    last_seen = models.DateTimeField(default=timezone.now, verbose_name='最後活動')
    client_session_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, null=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    active_seconds = models.PositiveIntegerField(default=0)
    end_reason = models.CharField(max_length=30, blank=True)
    user_agent = models.TextField(blank=True)

    class Meta:
        verbose_name = '使用時段'
        verbose_name_plural = '使用時段'
        ordering = ['-started_at']
        indexes = [models.Index(fields=['student', 'started_at'])]

    @property
    def duration_minutes(self):
        delta = (self.last_seen - self.started_at).total_seconds() / 60
        return max(0, round(delta, 1))

    def __str__(self):
        return f'{self.student.username} {self.started_at:%Y-%m-%d %H:%M} ({self.duration_minutes}m)'


class StudentUnitSummary(models.Model):
    """給人看的彙總表：一列＝一個學生 × 一個單元。

    由交卷（SubmitAttemptView）與教材心跳（ActivityPingView）即時更新，
    也可用 `python manage.py rebuild_unit_summaries` 從原始資料整表重算。
    """
    student = models.ForeignKey(User, on_delete=models.PROTECT, related_name='unit_summaries', verbose_name='學生')
    unit_number = models.PositiveIntegerField(verbose_name='單元編號')
    current_level = models.IntegerField(default=2, verbose_name='目前等級')
    attempt_count = models.PositiveIntegerField(default=0, verbose_name='作答次數')
    latest_score = models.FloatField(null=True, blank=True, verbose_name='最近分數')
    best_score = models.FloatField(null=True, blank=True, verbose_name='最佳分數')
    time_spent_seconds = models.PositiveIntegerField(default=0, verbose_name='教材停留(秒)')
    last_activity_at = models.DateTimeField(null=True, blank=True, verbose_name='最後活動時間')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '學生單元彙總'
        verbose_name_plural = '學生單元彙總'
        unique_together = ('student', 'unit_number')
        ordering = ['student__username', 'unit_number']
        constraints = [
            models.CheckConstraint(
                condition=models.Q(unit_number__gte=1, unit_number__lte=8),
                name='summary_unit_between_1_and_8',
            ),
        ]

    def __str__(self):
        return f'{self.student.username} Unit{self.unit_number} ({self.latest_score})'


class UnitRelease(models.Model):
    """單元開放開關：老師手動控制哪些單元對學生開放（取代自動解鎖）。"""
    unit_number = models.PositiveIntegerField(unique=True, verbose_name='單元編號')
    is_open = models.BooleanField(default=False, verbose_name='是否開放')
    opened_at = models.DateTimeField(null=True, blank=True, verbose_name='開放時間')
    opened_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='opened_units', verbose_name='操作者')

    class Meta:
        verbose_name = '單元開放'
        verbose_name_plural = '單元開放'
        ordering = ['unit_number']
        constraints = [
            models.CheckConstraint(
                condition=models.Q(unit_number__gte=1, unit_number__lte=8),
                name='release_unit_between_1_and_8',
            ),
        ]

    def __str__(self):
        return f'Unit {self.unit_number} {"開放" if self.is_open else "關閉"}'


class StudentEvent(models.Model):
    """Immutable, fine-grained student activity log. Aggregates are derived from it."""
    event_uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    student = models.ForeignKey(User, on_delete=models.PROTECT, related_name='events')
    session = models.ForeignKey(StudySession, on_delete=models.PROTECT, null=True, blank=True,
                                related_name='events')
    event_type = models.CharField(max_length=50, db_index=True)
    occurred_at = models.DateTimeField(default=timezone.now, db_index=True)
    received_at = models.DateTimeField(auto_now_add=True)
    course = models.ForeignKey(Course, on_delete=models.PROTECT, null=True, blank=True)
    lesson = models.ForeignKey(Lesson, on_delete=models.PROTECT, null=True, blank=True)
    quiz = models.ForeignKey('assessments.Quiz', on_delete=models.PROTECT, null=True, blank=True)
    question = models.ForeignKey('assessments.Question', on_delete=models.PROTECT, null=True, blank=True)
    recommendation = models.ForeignKey(AdaptiveRecommendation, on_delete=models.PROTECT,
                                       null=True, blank=True)
    page_url = models.CharField(max_length=1000, blank=True)
    referrer = models.CharField(max_length=1000, blank=True)
    duration_ms = models.PositiveBigIntegerField(default=0)
    sequence_number = models.PositiveIntegerField(null=True, blank=True)
    client_timezone = models.CharField(max_length=50, blank=True)
    app_version = models.CharField(max_length=50, blank=True)
    content_version = models.CharField(max_length=50, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['-occurred_at', '-id']
        indexes = [
            models.Index(fields=['student', 'occurred_at']),
            models.Index(fields=['student', 'event_type', 'occurred_at']),
            models.Index(fields=['lesson', 'occurred_at']),
        ]

    def __str__(self):
        return f'{self.student} {self.event_type} {self.occurred_at}'
