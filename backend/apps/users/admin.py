from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField, ReadOnlyPasswordHashWidget, UserChangeForm
from django.utils.html import format_html
from .models import User


class HiddenPasswordHashWidget(ReadOnlyPasswordHashWidget):
    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['summary'] = [{'label': '密碼雜湊資訊已隱藏。'}]
        return context


class CustomUserChangeForm(UserChangeForm):
    # password = ReadOnlyPasswordHashField(label='密碼')
    password = ReadOnlyPasswordHashField(label='密碼', widget=HiddenPasswordHashWidget)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    list_display = ('username', 'email', 'role_badge', 'student_id', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active')
    search_fields = ('username', 'email', 'student_id')
    ordering = ('role', 'username')
    list_editable = ('is_active',)
    fieldsets = UserAdmin.fieldsets + (
        ('額外資訊', {'fields': ('role', 'student_id', 'avatar', 'bio')}),
    )
    actions = [
        'delete_student_all_data',
        'deactivate_users',
        'activate_users',
    ]

    @admin.display(description='角色', ordering='role')
    def role_badge(self, obj):
        colors = {'student': '#c6f6d5', 'teacher': '#bee3f8', 'admin': '#fed7d7'}
        labels = {'student': '學生', 'teacher': '教師', 'admin': '管理員'}
        bg = colors.get(obj.role, '#eee')
        label = labels.get(obj.role, obj.role)
        return format_html('<span style="background:{};padding:2px 8px;border-radius:4px;font-size:0.8em">{}</span>', bg, label)

    @admin.action(description='🗑 刪除選取學生的所有學習資料（作答、路徑、推薦）')
    def delete_student_all_data(self, request, queryset):
        from apps.assessments.models import QuizAttempt
        from apps.learning.models import AdaptiveLearningPath, AdaptiveRecommendation, LearningProgress

        students = queryset.filter(role='student')
        count = students.count()
        if not count:
            self.message_user(request, '請選取學生帳號（role=student）。', level='warning')
            return

        QuizAttempt.objects.filter(student__in=students).delete()
        AdaptiveLearningPath.objects.filter(student__in=students).delete()
        AdaptiveRecommendation.objects.filter(student__in=students).delete()
        LearningProgress.objects.filter(student__in=students).delete()
        self.message_user(request, f'已清除 {count} 位學生的所有學習資料（帳號保留）。')

    @admin.action(description='⏸ 停用選取帳號')
    def deactivate_users(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f'已停用 {queryset.count()} 個帳號。')

    @admin.action(description='▶ 啟用選取帳號')
    def activate_users(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f'已啟用 {queryset.count()} 個帳號。')
