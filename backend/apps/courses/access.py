"""Server-side access rules for adaptive course content."""


def can_access_lesson(request, lesson) -> bool:
    """Return whether the authenticated request may open a lesson or its quiz.

    單元是否開放由老師手動控制（UnitRelease），不再依前一單元作答自動解鎖。
    """
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

    if not lesson.course.is_active:
        return False

    from apps.learning.models import UnitRelease

    return UnitRelease.objects.filter(unit_number=lesson.order, is_open=True).exists()
