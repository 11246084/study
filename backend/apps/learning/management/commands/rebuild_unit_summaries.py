"""從原始資料整表重算 StudentUnitSummary（彙總層可隨時丟棄重建）。"""
from django.core.management.base import BaseCommand

from apps.learning import summaries
from apps.users.models import User


class Command(BaseCommand):
    help = '由作答紀錄、閱讀進度與適性路徑重算所有學生的單元彙總表。'

    def handle(self, *args, **options):
        students = User.objects.filter(role='student')
        for student in students:
            summaries.rebuild_for_student(student)
        self.stdout.write(self.style.SUCCESS(
            f'已重算 {students.count()} 位學生的單元彙總。'
        ))
