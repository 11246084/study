from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from .models import Course, Lesson
from .serializers import CourseSerializer, CourseDetailSerializer, LessonDetailSerializer
from .access import can_access_lesson


class CourseListView(generics.ListAPIView):
    queryset = Course.objects.filter(is_active=True)
    serializer_class = CourseSerializer
    permission_classes = [permissions.AllowAny]


class CourseDetailView(generics.RetrieveAPIView):
    queryset = Course.objects.filter(is_active=True)
    serializer_class = CourseDetailSerializer
    permission_classes = [permissions.AllowAny]


class LessonDetailView(generics.RetrieveAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        lesson = super().get_object()
        if not can_access_lesson(self.request, lesson):
            if not lesson.course.is_active:
                raise PermissionDenied('課程尚未開放，請等待管理者開啟。')
            raise PermissionDenied('此單元尚未開放，請等待老師開放。')
        return lesson
