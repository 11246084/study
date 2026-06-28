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
    is_ready_for_submission = serializers.SerializerMethodField()

    class Meta:
        model = Quiz
        fields = ('id', 'title', 'quiz_type', 'pass_score', 'question_count',
                  'is_ready_for_submission', 'questions')

    def get_question_count(self, obj):
        return obj.questions.count()

    def get_is_ready_for_submission(self, obj):
        return all(
            question.question_type != 'coding' or bool(question.correct_answer.strip())
            for question in obj.questions.all()
        )


class AnswerSubmitSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    student_answer = serializers.CharField(allow_blank=True, trim_whitespace=False)


class AttemptSubmitSerializer(serializers.Serializer):
    quiz_id = serializers.IntegerField()
    answers = AnswerSubmitSerializer(many=True)


class QuizAttemptSerializer(serializers.ModelSerializer):
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)

    class Meta:
        model = QuizAttempt
        fields = ('id', 'quiz', 'quiz_title', 'score', 'is_passed', 'started_at', 'completed_at')
