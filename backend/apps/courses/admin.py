from django.contrib import admin
from django.utils.html import format_html
from .models import Course, Lesson, Enrollment


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 0
    fields = ('order', 'title', 'lesson_type', 'duration_minutes')
    ordering = ('order',)
    show_change_link = True


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'difficulty_badge', 'teacher', 'lesson_count', 'is_active', 'created_at')
    list_filter = ('difficulty', 'is_active')
    search_fields = ('title', 'teacher__username')
    list_editable = ('is_active',)
    ordering = ('difficulty', 'title')
    inlines = [LessonInline]
    actions = ['delete_with_all_data', 'deactivate_courses', 'activate_courses']

    @admin.display(description='難度', ordering='difficulty')
    def difficulty_badge(self, obj):
        colors = {'beginner': '#c6f6d5', 'intermediate': '#bee3f8', 'advanced': '#fed7d7'}
        labels = {'beginner': 'Level 1 補救', 'intermediate': 'Level 2 標準', 'advanced': 'Level 3 進階'}
        bg = colors.get(obj.difficulty, '#eee')
        label = labels.get(obj.difficulty, obj.difficulty)
        return format_html('<span style="background:{};padding:2px 8px;border-radius:4px;font-size:0.8em">{}</span>', bg, label)

    @admin.display(description='單元數')
    def lesson_count(self, obj):
        return obj.lessons.count()

    @admin.action(description='🗑 刪除選取課程（含所有單元、評量、題目）')
    def delete_with_all_data(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f'已刪除 {count} 門課程及所有相關資料。')

    @admin.action(description='⏸ 停用選取課程')
    def deactivate_courses(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f'已停用 {queryset.count()} 門課程。')

    @admin.action(description='▶ 啟用選取課程')
    def activate_courses(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f'已啟用 {queryset.count()} 門課程。')


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('order', 'title', 'course_difficulty', 'course', 'lesson_type', 'duration_minutes')
    list_filter = ('lesson_type', 'course__difficulty')
    search_fields = ('title', 'course__title')
    ordering = ('course__difficulty', 'order')

    @admin.display(description='難度', ordering='course__difficulty')
    def course_difficulty(self, obj):
        labels = {'beginner': 'L1', 'intermediate': 'L2', 'advanced': 'L3'}
        return labels.get(obj.course.difficulty, '?')


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'enrolled_at', 'progress')
    list_filter = ('course__difficulty',)
    search_fields = ('student__username', 'course__title')
    actions = ['delete_selected_enrollments']

    @admin.action(description='🗑 刪除選取的選課記錄')
    def delete_selected_enrollments(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f'已刪除 {count} 筆選課記錄。')
