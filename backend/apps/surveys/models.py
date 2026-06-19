from django.db import models
from apps.users.models import User


class SurveyScale(models.Model):
    """問卷構念（量表）定義。

    紙本問卷由研究者發放，老師把每位學生的「構念分數」登錄進系統，
    報表再依 phase 算前→後測變化。本表只定義構念，不存題目。
    higher_is_better=False 用於焦慮這類「分數越低越好」的構念。
    post_only=True 用於系統可行性這類只在後測施測的量表。
    """
    key = models.SlugField(max_length=50, unique=True, verbose_name='代碼')
    name = models.CharField(max_length=100, verbose_name='構念名稱')
    group = models.CharField(max_length=100, blank=True, verbose_name='所屬量表',
                             help_text='例如動機的四個子構面可填「學習動機」以利分組顯示')
    description = models.CharField(max_length=500, blank=True, verbose_name='說明')
    score_min = models.FloatField(default=1.0, verbose_name='分數下限')
    score_max = models.FloatField(default=5.0, verbose_name='分數上限')
    higher_is_better = models.BooleanField(default=True, verbose_name='高分代表較好',
                                           help_text='焦慮這類「越低越好」請取消勾選')
    post_only = models.BooleanField(default=False, verbose_name='僅後測',
                                    help_text='只在後測施測（如系統可行性量表）')
    order = models.PositiveIntegerField(default=0, verbose_name='排序')
    is_active = models.BooleanField(default=True, verbose_name='啟用')

    class Meta:
        verbose_name = '問卷構念'
        verbose_name_plural = '問卷構念'
        ordering = ['order', 'id']

    def __str__(self):
        return self.name


class SurveyScore(models.Model):
    """單一學生在某構念、某階段（前測/後測）的問卷分數。"""
    PHASE_CHOICES = [
        ('pre', '前測'),
        ('post', '後測'),
    ]
    student = models.ForeignKey(User, on_delete=models.PROTECT, related_name='survey_scores', verbose_name='學生')
    scale = models.ForeignKey(SurveyScale, on_delete=models.PROTECT, related_name='scores', verbose_name='構念')
    phase = models.CharField(max_length=10, choices=PHASE_CHOICES, verbose_name='階段')
    score = models.FloatField(verbose_name='分數')
    note = models.CharField(max_length=200, blank=True, verbose_name='備註')
    recorded_at = models.DateTimeField(auto_now=True, verbose_name='登錄時間')

    class Meta:
        verbose_name = '問卷成績'
        verbose_name_plural = '問卷成績'
        unique_together = ('student', 'scale', 'phase')
        ordering = ['scale__order', 'phase', 'student__username']

    def __str__(self):
        return f'{self.student.username} - {self.scale.name} ({self.get_phase_display()}) {self.score}'
