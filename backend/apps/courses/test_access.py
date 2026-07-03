from types import SimpleNamespace

from django.test import TestCase

from apps.learning.models import UnitRelease
from .access import can_access_lesson


class CourseAvailabilityAccessTests(TestCase):
    def _request(self, role='student'):
        user = SimpleNamespace(
            is_authenticated=True,
            role=role,
            is_staff=False,
            is_superuser=False,
        )
        return SimpleNamespace(user=user)

    def _lesson(self, is_active, order=1):
        return SimpleNamespace(order=order, course=SimpleNamespace(is_active=is_active))

    def test_student_cannot_open_closed_course(self):
        UnitRelease.objects.create(unit_number=1, is_open=True)
        self.assertFalse(can_access_lesson(self._request(), self._lesson(False)))

    def test_student_can_open_released_unit_of_active_course(self):
        UnitRelease.objects.create(unit_number=1, is_open=True)
        self.assertTrue(can_access_lesson(self._request(), self._lesson(True)))

    def test_student_cannot_open_unreleased_unit(self):
        UnitRelease.objects.create(unit_number=1, is_open=False)
        self.assertFalse(can_access_lesson(self._request(), self._lesson(True)))

    def test_admin_can_preview_closed_course(self):
        self.assertTrue(can_access_lesson(self._request('admin'), self._lesson(False)))
