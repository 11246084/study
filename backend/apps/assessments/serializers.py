from rest_framework import serializers
from .models import Quiz, Question, Choice, QuizAttempt, Answer


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ('id', 'content')


class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ('id', 'content', 'question_type', 'points', 'order', 'choices')


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    question_count = serializers.SerializerMethodField()

    class Meta:
        model = Quiz
        fields = ('id', 'title', 'quiz_type', 'pass_score', 'question_count', 'questions')

    def get_question_count(self, obj):
        return obj.questions.count()


class AnswerSubmitSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    student_answer = serializers.CharField()


class AttemptSubmitSerializer(serializers.Serializer):
    quiz_id = serializers.IntegerField()
    answers = AnswerSubmitSerializer(many=True)


class QuizAttemptSerializer(serializers.ModelSerializer):
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)

    class Meta:
        model = QuizAttempt
        fields = ('id', 'quiz', 'quiz_title', 'score', 'is_passed', 'started_at', 'completed_at')
