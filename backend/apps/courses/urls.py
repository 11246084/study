from django.urls import path
from .views import CourseListView, CourseDetailView, LessonDetailView

urlpatterns = [
    path('', CourseListView.as_view(), name='course-list'),
    path('<int:pk>/', CourseDetailView.as_view(), name='course-detail'),
    path('lesson/<int:pk>/', LessonDetailView.as_view(), name='lesson-detail'),
]
