from rest_framework import serializers
from .models import SurveyScale, SurveyScore


class SurveyScaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyScale
        fields = ('id', 'key', 'name', 'group', 'description',
                  'score_min', 'score_max', 'higher_is_better', 'post_only', 'order')


class SurveyScoreSerializer(serializers.ModelSerializer):
    scale_key = serializers.CharField(source='scale.key', read_only=True)
    scale_name = serializers.CharField(source='scale.name', read_only=True)
    username = serializers.CharField(source='student.username', read_only=True)

    class Meta:
        model = SurveyScore
        fields = ('id', 'student', 'username', 'scale', 'scale_key', 'scale_name',
                  'phase', 'score', 'note', 'recorded_at')
