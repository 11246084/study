from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ('student', '學生'),
        ('teacher', '教師'),
        ('admin', '管理員'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    student_id = models.CharField(max_length=20, blank=True, verbose_name='學號')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name='頭像')
    bio = models.TextField(blank=True, verbose_name='自我介紹')

    class Meta:
        verbose_name = '使用者'
        verbose_name_plural = '使用者'

    def __str__(self):
        return f'{self.username} ({self.get_role_display()})'
