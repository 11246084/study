from django.urls import path
from .views import CourseListView, CourseDetailView, EnrollView, MyCoursesView, LessonDetailView

urlpatterns = [
    path('', CourseListView.as_view(), name='course-list'),
    path('<int:pk>/', CourseDetailView.as_view(), name='course-detail'),
    path('enroll/', EnrollView.as_view(), name='enroll'),
    path('my/', MyCoursesView.as_view(), name='my-courses'),
    path('lesson/<int:pk>/', LessonDetailView.as_view(), name='lesson-detail'),
]
