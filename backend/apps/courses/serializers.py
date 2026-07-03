from rest_framework import serializers
from .models import Course, Lesson


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ('id', 'title', 'order', 'duration_minutes')


class LessonDetailSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    course_id = serializers.IntegerField(source='course.id', read_only=True)
    course_difficulty = serializers.CharField(source='course.difficulty', read_only=True)

    class Meta:
        model = Lesson
        fields = ('id', 'title', 'content', 'order',
                  'duration_minutes', 'course_id', 'course_title', 'course_difficulty')


class CourseSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.username', read_only=True)
    lesson_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ('id', 'title', 'description', 'teacher_name', 'difficulty',
                  'is_active', 'lesson_count', 'created_at')

    def get_lesson_count(self, obj):
        return obj.lessons.count()


class CourseDetailSerializer(CourseSerializer):
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta(CourseSerializer.Meta):
        fields = CourseSerializer.Meta.fields + ('lessons',)
