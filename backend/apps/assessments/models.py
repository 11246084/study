from django.db import models
from django.core.exceptions import ValidationError
from apps.users.models import User
from apps.courses.models import Lesson
import uuid


class Quiz(models.Model):
    QUIZ_TYPE_CHOICES = [
        ('formative', '形成性評量'),
        ('summative', '總結性評量'),
    ]
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='quizzes', verbose_name='所屬單元')
    title = models.CharField(max_length=200, verbose_name='評量名稱')
    quiz_type = models.CharField(max_length=20, choices=QUIZ_TYPE_CHOICES, default='formative', verbose_name='評量類型')
    pass_score = models.FloatField(default=60.0, verbose_name='及格分數')
    created_at = models.DateTimeField(auto_now_add=True)
    content_version = models.CharField(max_length=50, default='v1')

    class Meta:
        verbose_name = '評量'
        verbose_name_plural = '評量'

    def __str__(self):
        return f'{self.title} ({self.get_quiz_type_display()})'


class Question(models.Model):
    QUESTION_TYPE_CHOICES = [
        ('multiple_choice', '選擇題'),
        ('true_false', '是非題'),
        ('short_answer', '簡答題'),
        ('coding', '程式題'),
        ('fill_blank', '程式填空題'),
    ]
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions', verbose_name='所屬評量')
    content = models.TextField(verbose_name='題目內容')
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES, verbose_name='題型')
    correct_answer = models.TextField(
        blank=True,
        verbose_name='正確答案（填空/程式題用）',
        help_text='程式題：多個可接受答案以獨立一行 ---OR--- 分隔，比對忽略空白與大小寫。'
                  '填空題：題目內文以 __1__、__2__ 標記空格，每行對應一格答案，同格多解以 ||| 分隔。',
    )
    points = models.FloatField(default=10.0, verbose_name='配分')
    order = models.PositiveIntegerField(default=0, verbose_name='順序')
    explanation = models.TextField(blank=True, verbose_name='解析')
    content_version = models.CharField(max_length=50, default='v1')
    concept = models.CharField(max_length=80, blank=True, db_index=True, verbose_name='概念標籤')
    pattern = models.CharField(max_length=80, blank=True, db_index=True, verbose_name='題型模式')

    class Meta:
        verbose_name = '題目'
        verbose_name_plural = '題目'
        ordering = ['order']

    def __str__(self):
        return f'Q{self.order}: {self.content[:50]}'

    def clean(self):
        if self.question_type == 'coding' and not self.correct_answer.strip():
            raise ValidationError({'correct_answer': '程式題必須至少設定一個標準答案。'})
        if self.question_type == 'fill_blank':
            if not self.correct_answer.strip():
                raise ValidationError({'correct_answer': '填空題必須設定每格答案（一行一格）。'})
            if '__1__' not in self.content:
                raise ValidationError({'content': '填空題內文必須包含 __1__ 等空格標記。'})


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices', verbose_name='所屬題目')
    content = models.CharField(max_length=500, verbose_name='選項內容')
    is_correct = models.BooleanField(default=False, verbose_name='是否正確')

    class Meta:
        verbose_name = '選項'
        verbose_name_plural = '選項'


class QuizAttempt(models.Model):
    student = models.ForeignKey(User, on_delete=models.PROTECT, related_name='attempts', verbose_name='學生')
    quiz = models.ForeignKey(Quiz, on_delete=models.PROTECT, related_name='attempts', verbose_name='評量')
    score = models.FloatField(default=0.0, verbose_name='得分')
    is_passed = models.BooleanField(default=False, verbose_name='是否通過')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    attempt_uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, null=True)
    last_activity_at = models.DateTimeField(null=True, blank=True)
    abandoned_at = models.DateTimeField(null=True, blank=True)
    pass_score_snapshot = models.FloatField(null=True, blank=True)
    content_version = models.CharField(max_length=50, default='v1')
    selected_question_ids = models.JSONField(default=list, blank=True)

    class Meta:
        verbose_name = '作答記錄'
        verbose_name_plural = '作答記錄'
        constraints = [
            models.CheckConstraint(
                condition=models.Q(score__gte=0, score__lte=100),
                name='attempt_score_between_0_and_100',
            ),
        ]

    def __str__(self):
        return f'{self.student.username} - {self.quiz.title} ({self.score}分)'


class Answer(models.Model):
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='answers', verbose_name='作答記錄')
    question = models.ForeignKey(Question, on_delete=models.PROTECT, verbose_name='題目')
    student_answer = models.TextField(verbose_name='學生作答')
    is_correct = models.BooleanField(default=False, verbose_name='是否正確')
    points_earned = models.FloatField(default=0.0, verbose_name='獲得分數')

    class Meta:
        verbose_name = '答案'
        verbose_name_plural = '答案'


class QuestionInteraction(models.Model):
    """Per-question timing and answer revision history summary."""
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE,
                                related_name='question_interactions')
    question = models.ForeignKey(Question, on_delete=models.PROTECT,
                                 related_name='interactions')
    first_viewed_at = models.DateTimeField(null=True, blank=True)
    last_viewed_at = models.DateTimeField(null=True, blank=True)
    first_answered_at = models.DateTimeField(null=True, blank=True)
    last_answered_at = models.DateTimeField(null=True, blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    duration_ms = models.PositiveBigIntegerField(default=0)
    answer_revision_count = models.PositiveIntegerField(default=0)
    final_answer = models.TextField(blank=True)

    class Meta:
        unique_together = ('attempt', 'question')
        ordering = ['attempt', 'question__order']

    def __str__(self):
        return f'{self.attempt_id} / Q{self.question_id}'
