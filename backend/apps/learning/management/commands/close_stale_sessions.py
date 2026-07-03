"""把逾時但未關閉的使用時段補上明確結束紀錄（跑報表前執行）。"""
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.learning.models import StudySession


class Command(BaseCommand):
    help = '將最後活動超過 GAP_MINUTES 且未結束的 StudySession 標記 ended_at / end_reason=timeout。'

    def handle(self, *args, **options):
        cutoff = timezone.now() - timedelta(minutes=StudySession.GAP_MINUTES)
        stale = StudySession.objects.filter(ended_at__isnull=True, last_seen__lt=cutoff)
        count = 0
        for session in stale:
            session.ended_at = session.last_seen
            session.end_reason = 'timeout'
            session.save(update_fields=['ended_at', 'end_reason'])
            count += 1
        self.stdout.write(self.style.SUCCESS(f'已補關 {count} 段逾時的使用時段。'))
