from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from .models import Course, Lesson, Enrollment
from .serializers import CourseSerializer, CourseDetailSerializer, EnrollmentSerializer, LessonDetailSerializer
from .access import can_access_lesson


class CourseListView(generics.ListAPIView):
    queryset = Course.objects.filter(is_active=True)
    serializer_class = CourseSerializer
    permission_classes = [permissions.AllowAny]


class CourseDetailView(generics.RetrieveAPIView):
    queryset = Course.objects.filter(is_active=True)
    serializer_class = CourseDetailSerializer
    permission_classes = [permissions.AllowAny]


class EnrollView(generics.CreateAPIView):
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)


class MyCoursesView(generics.ListAPIView):
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Enrollment.objects.filter(student=self.request.user)


class LessonDetailView(generics.RetrieveAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        lesson = super().get_object()
        if not can_access_lesson(self.request, lesson):
            raise PermissionDenied('請先完成前一單元評量。')
        return lesson
