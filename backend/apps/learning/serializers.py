from rest_framework import serializers
from .models import LearningProgress, AdaptiveRecommendation, UnitRelease


class LearningProgressSerializer(serializers.ModelSerializer):
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)
    course_title = serializers.CharField(source='lesson.course.title', read_only=True)

    class Meta:
        model = LearningProgress
        fields = ('id', 'lesson', 'lesson_title', 'course_title',
                  'status', 'time_spent_seconds', 'last_accessed', 'completed_at')
        read_only_fields = ('time_spent_seconds', 'last_accessed')


class RecommendationSerializer(serializers.ModelSerializer):
    lesson_title = serializers.CharField(source='recommended_lesson.title', read_only=True)
    lesson_id = serializers.IntegerField(source='recommended_lesson.id', read_only=True)
    course_title = serializers.CharField(source='recommended_lesson.course.title', read_only=True)
    is_open = serializers.SerializerMethodField()

    class Meta:
        model = AdaptiveRecommendation
        fields = ('id', 'lesson_id', 'lesson_title', 'course_title', 'reason',
                  'created_at', 'is_dismissed', 'is_open')

    def get_is_open(self, obj):
        return UnitRelease.objects.filter(
            unit_number=obj.recommended_lesson.order, is_open=True).exists()
