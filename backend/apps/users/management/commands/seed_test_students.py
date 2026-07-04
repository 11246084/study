"""Create disposable student accounts for load testing.

Usage (run from backend/):
    python manage.py seed_test_students --count 55
    python manage.py seed_test_students --count 55 --delete   # tear down afterwards

Accounts are loadtest001 ... loadtestNNN, password "loadtest-pw".
They are marked with a recognisable username prefix so you can wipe them
before real data collection. DO NOT run this against a production DB that
already holds real research data without --delete cleanup afterwards.
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.users.models import User

PREFIX = 'loadtest'
PASSWORD = 'loadtest-pw'


class Command(BaseCommand):
    help = 'Create (or delete) throwaway student accounts for load testing.'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=55, help='How many test students')
        parser.add_argument('--delete', action='store_true', help='Delete all loadtest* accounts instead')

    def handle(self, *args, **options):
        if options['delete']:
            deleted, _ = User.objects.filter(username__startswith=PREFIX).delete()
            self.stdout.write(self.style.SUCCESS(f'Deleted loadtest accounts (rows removed: {deleted}).'))
            return

        count = options['count']
        created = 0
        with transaction.atomic():
            for i in range(1, count + 1):
                username = f'{PREFIX}{i:03d}'
                if User.objects.filter(username=username).exists():
                    continue
                user = User(username=username, role='student', first_name=f'壓測學生{i:03d}')
                # test accounts skip the forced password change if that field exists
                if hasattr(user, 'must_change_password'):
                    user.must_change_password = False
                user.set_password(PASSWORD)
                user.save()
                created += 1
        self.stdout.write(self.style.SUCCESS(
            f'Ready: {count} test students exist (newly created: {created}). '
            f'Login as {PREFIX}001..{PREFIX}{count:03d} / password "{PASSWORD}". '
            f'Run with --delete to remove them before real data collection.'
        ))
