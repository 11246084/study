"""Server-side access rules for adaptive course content."""


def can_access_lesson(request, lesson) -> bool:
    """Return whether the authenticated request may open a lesson or its quiz."""
    user = request.user
    if not user or not user.is_authenticated:
        return False

    if (
        getattr(request, 'preview_as_admin', False)
        or getattr(user, 'role', None) in {'teacher', 'admin'}
        or user.is_staff
        or user.is_superuser
    ):
        return True

    if lesson.order <= 1:
        return True

    from apps.assessments.models import QuizAttempt

    return QuizAttempt.objects.filter(
        student=user,
        quiz__lesson__order=lesson.order - 1,
        completed_at__isnull=False,
    ).exists()
