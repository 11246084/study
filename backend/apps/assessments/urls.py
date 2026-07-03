from django.urls import path
from .views import (QuizDetailView, SubmitAttemptView, MyAttemptsView, LessonQuizListView,
                    AttemptDetailView, StartAttemptView, QuestionInteractionView,
                    AbandonAttemptView)

urlpatterns = [
    path('<int:pk>/', QuizDetailView.as_view(), name='quiz-detail'),
    path('submit/', SubmitAttemptView.as_view(), name='submit-attempt'),
    path('start/', StartAttemptView.as_view(), name='start-attempt'),
    path('interaction/', QuestionInteractionView.as_view(), name='question-interaction'),
    path('attempts/<int:pk>/abandon/', AbandonAttemptView.as_view(), name='abandon-attempt'),
    path('my-attempts/', MyAttemptsView.as_view(), name='my-attempts'),
    path('lesson/<int:lesson_id>/', LessonQuizListView.as_view(), name='lesson-quizzes'),
    path('attempts/<int:pk>/', AttemptDetailView.as_view(), name='attempt-detail'),
]
