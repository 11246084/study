from django.db.models import Avg, Count, Max, Q
from rest_framework import generics, permissions, response, views
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import User
from .serializers import RegisterSerializer, UserProfileSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class LoginView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class IsManagementUser(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and (user.role == 'admin' or user.is_staff or user.is_superuser)
        )


class StudentUsageView(views.APIView):
    permission_classes = [IsManagementUser]

    def get(self, request):
        from apps.assessments.models import QuizAttempt
        from apps.learning.models import AdaptiveLearningPath, AdaptiveRecommendation

        students = User.objects.filter(role='student').order_by('username')
        attempts_summary = {
            row['student_id']: row
            for row in QuizAttempt.objects.filter(completed_at__isnull=False)
            .values('student_id')
            .annotate(
                attempt_count=Count('id'),
                avg_score=Avg('score'),
                passed_count=Count('id', filter=Q(is_passed=True)),
                completed_units=Count('quiz__lesson__order', distinct=True),
                last_activity=Max('completed_at'),
            )
        }
        latest_paths = {}
        for path in AdaptiveLearningPath.objects.filter(student__role='student').order_by(
            'student_id',
            '-unit_number',
            '-updated_at',
        ):
            latest_paths.setdefault(path.student_id, path)
        active_recommendations = {
            row['student_id']: row['count']
            for row in AdaptiveRecommendation.objects.filter(
                student__role='student',
                is_dismissed=False,
            )
            .values('student_id')
            .annotate(count=Count('id'))
        }

        rows = []
        total_attempts = 0
        total_score_sum = 0
        total_score_count = 0
        active_students = 0
        completed_unit_sum = 0

        for student in students:
            summary = attempts_summary.get(student.id, {})
            attempt_count = summary.get('attempt_count') or 0
            avg_score = summary.get('avg_score')
            passed_count = summary.get('passed_count') or 0
            completed_units = summary.get('completed_units') or 0
            last_activity = summary.get('last_activity')
            pass_rate = round((passed_count / attempt_count) * 100, 1) if attempt_count else None
            latest_path = latest_paths.get(student.id)

            total_attempts += attempt_count
            completed_unit_sum += completed_units
            if avg_score is not None:
                total_score_sum += avg_score
                total_score_count += 1
            if last_activity:
                active_students += 1

            rows.append({
                'id': student.id,
                'username': student.username,
                'email': student.email,
                'student_id': student.student_id,
                'is_active': student.is_active,
                'date_joined': student.date_joined,
                'attempt_count': attempt_count,
                'completed_units': completed_units,
                'avg_score': round(avg_score, 1) if avg_score is not None else None,
                'pass_rate': pass_rate,
                'last_activity': last_activity,
                'current_unit': latest_path.unit_number if latest_path else None,
                'current_level': latest_path.current_level if latest_path else None,
                'active_recommendations': active_recommendations.get(student.id, 0),
            })

        student_count = students.count()
        overview = {
            'student_count': student_count,
            'active_students': active_students,
            'total_attempts': total_attempts,
            'avg_score': round(total_score_sum / total_score_count, 1) if total_score_count else None,
            'avg_completed_units': round(completed_unit_sum / student_count, 1) if student_count else 0,
        }
        return response.Response({'overview': overview, 'students': rows})
