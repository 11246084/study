from django.contrib import admin
from .models import SurveyScale, SurveyScore


@admin.register(SurveyScale)
class SurveyScaleAdmin(admin.ModelAdmin):
    list_display = ('name', 'order', 'group', 'key', 'score_min', 'score_max',
                    'higher_is_better', 'post_only', 'is_active')
    list_editable = ('order', 'is_active')
    list_filter = ('group', 'higher_is_better', 'post_only', 'is_active')
    search_fields = ('name', 'key', 'group')


@admin.register(SurveyScore)
class SurveyScoreAdmin(admin.ModelAdmin):
    list_display = ('student', 'scale', 'phase', 'score', 'recorded_at')
    list_filter = ('phase', 'scale')
    search_fields = ('student__username',)
    autocomplete_fields = ()
