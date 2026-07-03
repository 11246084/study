from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid


class User(AbstractUser):
    ROLE_CHOICES = [
        ('student', '學生'),
        ('teacher', '教師'),
        ('admin', '管理員'),
    ]
    GENDER_CHOICES = [
        ('male', '男'),
        ('female', '女'),
        ('other', '其他/不願透露'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    student_id = models.CharField(max_length=20, blank=True, verbose_name='學號')
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, verbose_name='性別')
    login_count = models.PositiveIntegerField(default=0, verbose_name='登入次數')
    school_short_name = models.CharField(max_length=100, blank=True, verbose_name='學校簡稱')
    school_name = models.CharField(max_length=200, blank=True, verbose_name='學校')
    preferred_programming_language = models.CharField(max_length=100, blank=True, verbose_name='預計使用的程式語言')
    import_note = models.CharField(max_length=500, blank=True, verbose_name='匯入備註')
    must_change_password = models.BooleanField(default=False, verbose_name='必須修改密碼')

    class Meta:
        verbose_name = '使用者'
        verbose_name_plural = '使用者'

    def __str__(self):
        return f'{self.username} ({self.get_role_display()})'


class LoginEvent(models.Model):
    """Append-only authentication history for research and auditing."""
    EVENT_CHOICES = [
        ('login_success', '登入成功'),
        ('login_failed', '登入失敗'),
        ('logout', '登出'),
    ]
    event_uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True,
                             related_name='login_events')
    username_attempt = models.CharField(max_length=150, blank=True)
    event_type = models.CharField(max_length=20, choices=EVENT_CHOICES)
    occurred_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    client_session_id = models.UUIDField(null=True, blank=True, db_index=True)

    class Meta:
        ordering = ['-occurred_at']
        indexes = [
            models.Index(fields=['user', 'occurred_at']),
            models.Index(fields=['event_type', 'occurred_at']),
        ]

    def __str__(self):
        return f'{self.event_type} {self.user or self.username_attempt} {self.occurred_at}'


class DataChangeAudit(models.Model):
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    model_label = models.CharField(max_length=100)
    object_pk = models.CharField(max_length=100)
    action = models.CharField(max_length=20)
    occurred_at = models.DateTimeField(auto_now_add=True)
    before = models.JSONField(default=dict, blank=True)
    after = models.JSONField(default=dict, blank=True)
    reason = models.CharField(max_length=500, blank=True)

    class Meta:
        ordering = ['-occurred_at']
        indexes = [models.Index(fields=['model_label', 'object_pk', 'occurred_at'])]
