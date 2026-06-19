from django.db import models
from apps.users.models import User
from apps.courses.models import Lesson


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
    ]
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions', verbose_name='所屬評量')
    content = models.TextField(verbose_name='題目內容')
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES, verbose_name='題型')
    correct_answer = models.TextField(blank=True, verbose_name='正確答案（填空/程式題用）')
    points = models.FloatField(default=10.0, verbose_name='配分')
    order = models.PositiveIntegerField(default=0, verbose_name='順序')
    explanation = models.TextField(blank=True, verbose_name='解析')

    class Meta:
        verbose_name = '題目'
        verbose_name_plural = '題目'
        ordering = ['order']

    def __str__(self):
        return f'Q{self.order}: {self.content[:50]}'


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

    class Meta:
        verbose_name = '作答記錄'
        verbose_name_plural = '作答記錄'

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
