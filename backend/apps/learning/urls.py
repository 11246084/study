from django.urls import path
from .views import (
    LearningProgressView, ProgressUpdateView, RecommendationListView,
    PerformanceListView, AdaptivePathView, RecommendationClickView, ActivityPingView,
    SessionHeartbeatView,
)

urlpatterns = [
    path('progress/', LearningProgressView.as_view(), name='learning-progress'),
    path('progress/<int:pk>/', ProgressUpdateView.as_view(), name='progress-update'),
    path('recommendations/', RecommendationListView.as_view(), name='recommendations'),
    path('recommendations/<int:pk>/click/', RecommendationClickView.as_view(), name='recommendation-click'),
    path('activity/', ActivityPingView.as_view(), name='activity-ping'),
    path('heartbeat/', SessionHeartbeatView.as_view(), name='session-heartbeat'),
    path('performance/', PerformanceListView.as_view(), name='performance'),
    path('adaptive-path/', AdaptivePathView.as_view(), name='adaptive-path'),
]
