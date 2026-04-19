from django.contrib import admin
from django.utils.html import format_html
from .models import LearningProgress, AdaptiveRecommendation, PerformanceRecord, AdaptiveLearningPath


@admin.register(AdaptiveLearningPath)
class AdaptivePathAdmin(admin.ModelAdmin):
    list_display = ('student', 'unit_number', 'level_badge', 'last_score', 'updated_at')
    list_filter = ('current_level',)
    search_fields = ('student__username',)
    ordering = ('student__username', 'unit_number')
    actions = ['reset_to_level2', 'delete_selected_paths']

    @admin.display(description='當前等級', ordering='current_level')
    def level_badge(self, obj):
        colors = {1: '#fed7d7', 2: '#c6f6d5', 3: '#bee3f8'}
        labels = {1: 'Level 1 補救', 2: 'Level 2 標準', 3: 'Level 3 進階'}
        bg = colors.get(obj.current_level, '#eee')
        label = labels.get(obj.current_level, str(obj.current_level))
        return format_html('<span style="background:{};padding:2px 8px;border-radius:4px;font-size:0.8em">{}</span>', bg, label)

    @admin.action(description='↩ 重設選取記錄至 Level 2（標準版）')
    def reset_to_level2(self, request, queryset):
        count = queryset.update(current_level=2, last_score=0.0)
        self.message_user(request, f'已將 {count} 筆學習路徑重設為 Level 2。')

    @admin.action(description='🗑 刪除選取的學習路徑記錄')
    def delete_selected_paths(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f'已刪除 {count} 筆適性學習路徑。')


@admin.register(AdaptiveRecommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ('student', 'unit_info', 'reason_short', 'is_dismissed', 'created_at')
    list_filter = ('is_dismissed',)
    search_fields = ('student__username', 'recommended_lesson__title')
    list_editable = ('is_dismissed',)
    ordering = ('-created_at',)
    actions = ['dismiss_all', 'delete_selected_recs', 'delete_dismissed']

    @admin.display(description='推薦單元')
    def unit_info(self, obj):
        diff_labels = {'beginner': 'L1', 'intermediate': 'L2', 'advanced': 'L3'}
        diff = diff_labels.get(obj.recommended_lesson.course.difficulty, '?')
        return f'[{diff}] Unit {obj.recommended_lesson.order} — {obj.recommended_lesson.title}'

    @admin.display(description='推薦原因')
    def reason_short(self, obj):
        return obj.reason[:50] + ('…' if len(obj.reason) > 50 else '')

    @admin.action(description='✓ 將選取推薦標記為已忽略')
    def dismiss_all(self, request, queryset):
        count = queryset.update(is_dismissed=True)
        self.message_user(request, f'已忽略 {count} 筆推薦。')

    @admin.action(description='🗑 刪除選取的推薦記錄')
    def delete_selected_recs(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f'已刪除 {count} 筆推薦記錄。')

    @admin.action(description='🗑 刪除所有「已忽略」的推薦記錄')
    def delete_dismissed(self, request, queryset):
        dismissed = queryset.filter(is_dismissed=True)
        count = dismissed.count()
        dismissed.delete()
        self.message_user(request, f'已刪除 {count} 筆已忽略的推薦。')


@admin.register(LearningProgress)
class LearningProgressAdmin(admin.ModelAdmin):
    list_display = ('student', 'lesson', 'status', 'time_spent', 'last_accessed')
    list_filter = ('status',)
    search_fields = ('student__username', 'lesson__title')
    actions = ['reset_to_not_started', 'delete_selected_progress']

    @admin.action(description='↩ 重設選取進度為「未開始」')
    def reset_to_not_started(self, request, queryset):
        count = queryset.update(status='not_started', time_spent=0)
        self.message_user(request, f'已重設 {count} 筆學習進度。')

    @admin.action(description='🗑 刪除選取的學習進度')
    def delete_selected_progress(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f'已刪除 {count} 筆學習進度。')


@admin.register(PerformanceRecord)
class PerformanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'quiz_score_avg', 'proficiency_badge', 'recorded_at')
    list_filter = ('proficiency',)
    search_fields = ('student__username', 'course__title')

    @admin.display(description='精熟度', ordering='proficiency')
    def proficiency_badge(self, obj):
        colors = {'high': '#c6f6d5', 'medium': '#eee', 'low': '#fed7d7'}
        labels = {'high': '精熟', 'medium': '普通', 'low': '待加強'}
        bg = colors.get(obj.proficiency, '#eee')
        label = labels.get(obj.proficiency, obj.proficiency)
        return format_html('<span style="background:{};padding:2px 8px;border-radius:4px;font-size:0.8em">{}</span>', bg, label)
