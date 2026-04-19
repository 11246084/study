from django.urls import path
from .views import LearningProgressView, ProgressUpdateView, RecommendationListView, PerformanceListView, AdaptivePathView

urlpatterns = [
    path('progress/', LearningProgressView.as_view(), name='learning-progress'),
    path('progress/<int:pk>/', ProgressUpdateView.as_view(), name='progress-update'),
    path('recommendations/', RecommendationListView.as_view(), name='recommendations'),
    path('performance/', PerformanceListView.as_view(), name='performance'),
    path('adaptive-path/', AdaptivePathView.as_view(), name='adaptive-path'),
]
