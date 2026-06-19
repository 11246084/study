from django.urls import path
from .views import (
    AdminDataView, ChangePasswordView, RegisterView, LoginView, ProfileView,
    StudentUsageView, ResearchAnalyticsView, MyReportView, SystemStatsView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('stats/', SystemStatsView.as_view(), name='system-stats'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('my-report/', MyReportView.as_view(), name='my-report'),
    path('admin/student-usage/', StudentUsageView.as_view(), name='admin-student-usage'),
    path('admin/research-analytics/', ResearchAnalyticsView.as_view(), name='admin-research-analytics'),
    path('admin/research-analytics/student/<int:pk>/', ResearchAnalyticsView.as_view(), name='admin-research-analytics-student'),
    path('admin/data/<str:key>/', AdminDataView.as_view(), name='admin-data-list'),
    path('admin/data/<str:key>/<int:pk>/', AdminDataView.as_view(), name='admin-data-detail'),
]
