from django.db import models
from apps.users.models import User


class Course(models.Model):
    DIFFICULTY_CHOICES = [
        ('beginner', '初級'),
        ('intermediate', '中級'),
        ('advanced', '進階'),
    ]
    title = models.CharField(max_length=200, verbose_name='課程名稱')
    description = models.TextField(verbose_name='課程描述')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='taught_courses', verbose_name='授課教師')
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='beginner', verbose_name='難度')
    cover_image = models.ImageField(upload_to='courses/', null=True, blank=True, verbose_name='封面圖')
    is_active = models.BooleanField(default=True, verbose_name='是否開放')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '課程'
        verbose_name_plural = '課程'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Lesson(models.Model):
    LESSON_TYPE_CHOICES = [
        ('video', '影片'),
        ('text', '閱讀'),
        ('exercise', '練習題'),
    ]
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons', verbose_name='所屬課程')
    title = models.CharField(max_length=200, verbose_name='單元名稱')
    content = models.TextField(verbose_name='內容')
    lesson_type = models.CharField(max_length=20, choices=LESSON_TYPE_CHOICES, default='text', verbose_name='單元類型')
    order = models.PositiveIntegerField(default=0, verbose_name='順序')
    duration_minutes = models.PositiveIntegerField(default=0, verbose_name='預估時間(分鐘)')

    class Meta:
        verbose_name = '單元'
        verbose_name_plural = '單元'
        ordering = ['order']

    def __str__(self):
        return f'{self.course.title} - {self.title}'


class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments', verbose_name='學生')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments', verbose_name='課程')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    progress = models.FloatField(default=0.0, verbose_name='進度(%)')

    class Meta:
        verbose_name = '選課紀錄'
        verbose_name_plural = '選課紀錄'
        unique_together = ('student', 'course')

    def __str__(self):
        return f'{self.student.username} - {self.course.title}'
