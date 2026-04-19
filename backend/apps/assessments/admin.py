from django.contrib import admin
from django.utils.html import format_html
from .models import Quiz, Question, Choice, QuizAttempt, Answer


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 0
    fields = ('content', 'is_correct')


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 0
    fields = ('order', 'question_type', 'content', 'points')
    ordering = ('order',)
    show_change_link = True


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    fields = ('question', 'student_answer', 'is_correct', 'points_earned')
    readonly_fields = ('question', 'student_answer', 'is_correct', 'points_earned')
    can_delete = True


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'lesson_unit', 'course_level', 'quiz_type', 'pass_score', 'question_count')
    list_filter = ('quiz_type', 'lesson__course__difficulty')
    search_fields = ('title', 'lesson__title')
    ordering = ('lesson__course__difficulty', 'lesson__order')
    inlines = [QuestionInline]
    actions = ['delete_quizzes_and_questions']

    @admin.display(description='單元', ordering='lesson__order')
    def lesson_unit(self, obj):
        return f'Unit {obj.lesson.order} — {obj.lesson.title}'

    @admin.display(description='等級', ordering='lesson__course__difficulty')
    def course_level(self, obj):
        labels = {'beginner': 'Level 1', 'intermediate': 'Level 2', 'advanced': 'Level 3'}
        return labels.get(obj.lesson.course.difficulty, '?')

    @admin.display(description='題數')
    def question_count(self, obj):
        return obj.questions.count()

    @admin.action(description='🗑 刪除選取評量（含所有題目與作答記錄）')
    def delete_quizzes_and_questions(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f'已刪除 {count} 份評量及所有相關題目與記錄。')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('order', 'short_content', 'quiz', 'question_type_badge', 'points')
    list_filter = ('question_type', 'quiz__lesson__course__difficulty')
    search_fields = ('content', 'quiz__title')
    ordering = ('quiz__lesson__course__difficulty', 'quiz__lesson__order', 'order')
    inlines = [ChoiceInline]

    @admin.display(description='題目內容')
    def short_content(self, obj):
        return obj.content[:60] + ('…' if len(obj.content) > 60 else '')

    @admin.display(description='題型')
    def question_type_badge(self, obj):
        colors = {'multiple_choice': '#c6f6d5', 'short_answer': '#bee3f8', 'coding': '#fed7d7'}
        labels = {'multiple_choice': '選擇題', 'short_answer': '填空題', 'coding': '程式題'}
        bg = colors.get(obj.question_type, '#eee')
        label = labels.get(obj.question_type, obj.question_type)
        return format_html('<span style="background:{};padding:2px 8px;border-radius:4px;font-size:0.8em">{}</span>', bg, label)


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('student', 'quiz_unit', 'score_badge', 'is_passed', 'started_at', 'completed_at')
    list_filter = ('is_passed', 'quiz__lesson__course__difficulty')
    search_fields = ('student__username', 'quiz__title')
    date_hierarchy = 'started_at'
    ordering = ('-started_at',)
    readonly_fields = ('student', 'quiz', 'score', 'is_passed', 'started_at', 'completed_at')
    inlines = [AnswerInline]
    actions = [
        'delete_selected_attempts',
        'delete_failed_attempts',
        'delete_all_attempts_for_student',
    ]

    @admin.display(description='評量', ordering='quiz__lesson__order')
    def quiz_unit(self, obj):
        diff_labels = {'beginner': 'L1', 'intermediate': 'L2', 'advanced': 'L3'}
        diff = diff_labels.get(obj.quiz.lesson.course.difficulty, '?')
        return f'[{diff}] Unit {obj.quiz.lesson.order} — {obj.quiz.lesson.title}'

    @admin.display(description='得分', ordering='score')
    def score_badge(self, obj):
        color = '#38a169' if obj.is_passed else '#e53e3e'
        return format_html('<span style="font-weight:700;color:{}">{:.0f} 分</span>', color, obj.score)

    @admin.action(description='🗑 刪除選取的作答記錄')
    def delete_selected_attempts(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f'已刪除 {count} 筆作答記錄。')

    @admin.action(description='🗑 刪除所有「未通過」的作答記錄')
    def delete_failed_attempts(self, request, queryset):
        failed = queryset.filter(is_passed=False)
        count = failed.count()
        failed.delete()
        self.message_user(request, f'已刪除 {count} 筆未通過的作答記錄。')

    @admin.action(description='🗑 刪除選取學生的全部作答記錄（含答案）')
    def delete_all_attempts_for_student(self, request, queryset):
        students = queryset.values_list('student', flat=True).distinct()
        from .models import QuizAttempt as QA
        deleted, _ = QA.objects.filter(student__in=students).delete()
        self.message_user(request, f'已清除 {len(students)} 位學生共 {deleted} 筆作答記錄。')
