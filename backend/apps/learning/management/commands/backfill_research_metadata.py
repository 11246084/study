import uuid

from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = 'Backfill research metadata without inventing historical activity events.'

    @transaction.atomic
    def handle(self, *args, **options):
        from apps.assessments.models import QuizAttempt
        from apps.learning.models import StudySession

        attempts = 0
        for attempt in QuizAttempt.objects.filter(attempt_uuid__isnull=True).iterator():
            attempt.attempt_uuid = uuid.uuid4()
            attempt.save(update_fields=['attempt_uuid'])
            attempts += 1

        sessions = 0
        for session in StudySession.objects.filter(client_session_id__isnull=True).iterator():
            session.client_session_id = uuid.uuid4()
            session.save(update_fields=['client_session_id'])
            sessions += 1

        self.stdout.write(self.style.SUCCESS(
            f'Backfilled attempts={attempts}, sessions={sessions}, '
            'No historical StudentEvent rows were fabricated.'
        ))
