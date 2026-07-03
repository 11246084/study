from django.urls import path
from .views import (
    LearningProgressView, ProgressUpdateView, RecommendationListView,
    AdaptivePathView, RecommendationClickView, ActivityPingView,
    SessionHeartbeatView,
    RecommendationImpressionView, RecommendationDismissView, EventBatchView,
    UnitReleaseView,
)

urlpatterns = [
    path('progress/', LearningProgressView.as_view(), name='learning-progress'),
    path('progress/<int:pk>/', ProgressUpdateView.as_view(), name='progress-update'),
    path('recommendations/', RecommendationListView.as_view(), name='recommendations'),
    path('recommendations/<int:pk>/click/', RecommendationClickView.as_view(), name='recommendation-click'),
    path('recommendations/<int:pk>/impression/', RecommendationImpressionView.as_view(), name='recommendation-impression'),
    path('recommendations/<int:pk>/dismiss/', RecommendationDismissView.as_view(), name='recommendation-dismiss'),
    path('activity/', ActivityPingView.as_view(), name='activity-ping'),
    path('heartbeat/', SessionHeartbeatView.as_view(), name='session-heartbeat'),
    path('events/', EventBatchView.as_view(), name='student-events'),
    path('adaptive-path/', AdaptivePathView.as_view(), name='adaptive-path'),
    path('unit-release/', UnitReleaseView.as_view(), name='unit-release'),
]
