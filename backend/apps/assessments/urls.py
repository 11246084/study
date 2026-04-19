from django.urls import path
from .views import QuizDetailView, SubmitAttemptView, MyAttemptsView, LessonQuizListView, AttemptDetailView

urlpatterns = [
    path('<int:pk>/', QuizDetailView.as_view(), name='quiz-detail'),
    path('submit/', SubmitAttemptView.as_view(), name='submit-attempt'),
    path('my-attempts/', MyAttemptsView.as_view(), name='my-attempts'),
    path('lesson/<int:lesson_id>/', LessonQuizListView.as_view(), name='lesson-quizzes'),
    path('attempts/<int:pk>/', AttemptDetailView.as_view(), name='attempt-detail'),
]
