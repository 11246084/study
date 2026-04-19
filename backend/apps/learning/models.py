from django.db import models
from apps.users.models import User
from apps.courses.models import Course, Lesson


class LearningProgress(models.Model):
    STATUS_CHOICES = [
        ('not_started', '未開始'),
        ('in_progress', '學習中'),
        ('completed', '已完成'),
    ]
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress', verbose_name='學生')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='progress', verbose_name='單元')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started', verbose_name='狀態')
    time_spent = models.PositiveIntegerField(default=0, verbose_name='花費時間(分鐘)')
    last_accessed = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = '學習進度'
        verbose_name_plural = '學習進度'
        unique_together = ('student', 'lesson')

    def __str__(self):
        return f'{self.student.username} - {self.lesson.title} ({self.get_status_display()})'


class AdaptiveRecommendation(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recommendations', verbose_name='學生')
    recommended_lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, verbose_name='推薦單元')
    reason = models.CharField(max_length=500, verbose_name='推薦原因')
    created_at = models.DateTimeField(auto_now_add=True)
    is_dismissed = models.BooleanField(default=False, verbose_name='是否忽略')

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
    分流規則：score >= 90 → 升階；score < 80 → 降階；80~89 → 維持
    """
    LEVEL_CHOICES = [
        (1, 'Level 1 補救版'),
        (2, 'Level 2 標準版'),
        (3, 'Level 3 進階版'),
    ]
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='adaptive_path', verbose_name='學生')
    unit_number = models.PositiveIntegerField(verbose_name='單元編號')
    current_level = models.IntegerField(choices=LEVEL_CHOICES, default=2, verbose_name='當前等級')
    last_score = models.FloatField(default=0.0, verbose_name='最近評量分數')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '適性學習路徑'
        verbose_name_plural = '適性學習路徑'
        unique_together = ('student', 'unit_number')
        ordering = ['unit_number']

    def __str__(self):
        return f'{self.student.username} Unit{self.unit_number} Lv{self.current_level}'

    @staticmethod
    def determine_next_level(current_level: int, score: float) -> int:
        """依分數決定下一單元的等級"""
        if score >= 90 and current_level < 3:
            return current_level + 1
        if score < 80 and current_level > 1:
            return current_level - 1
        return current_level


class PerformanceRecord(models.Model):
    PROFICIENCY_CHOICES = [
        ('low', '待加強'),
        ('medium', '普通'),
        ('high', '精熟'),
    ]
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='performance', verbose_name='學生')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name='課程')
    quiz_score_avg = models.FloatField(default=0.0, verbose_name='平均評量分數')
    proficiency = models.CharField(max_length=10, choices=PROFICIENCY_CHOICES, default='medium', verbose_name='精熟度')
    recorded_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '學習表現紀錄'
        verbose_name_plural = '學習表現紀錄'
        unique_together = ('student', 'course')
        ordering = ['course']
