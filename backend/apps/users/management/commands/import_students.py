import csv
import re
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.users.models import User


def normalize_header(value):
    return re.sub(r'\s+', '', (value or '')).casefold()


def normalize_phone(value):
    raw = (value or '').strip()
    digits = re.sub(r'\D', '', raw)
    if digits.startswith('886') and len(digits) >= 12:
        digits = '0' + digits[3:]
    elif len(digits) == 9 and digits.startswith('9'):
        digits = '0' + digits
    return digits


class Command(BaseCommand):
    help = 'Import student accounts from a UTF-8 CSV export.'

    def add_arguments(self, parser):
        parser.add_argument('file', help='Path to a UTF-8 CSV file')
        parser.add_argument('--dry-run', action='store_true', help='Validate without writing')
        parser.add_argument('--update-existing', action='store_true', help='Update matching student accounts')
        parser.add_argument(
            '--reset-passwords', action='store_true',
            help='With --update-existing, reset existing passwords to the phone number (or student ID when blank)',
        )

    def handle(self, *args, **options):
        path = Path(options['file'])
        if not path.exists() or not path.is_file():
            raise CommandError(f'File not found: {path}')
        if path.suffix.lower() not in {'.csv', '.txt'}:
            raise CommandError('Please export the spreadsheet as CSV UTF-8 first.')

        try:
            with path.open('r', encoding='utf-8-sig', newline='') as stream:
                reader = csv.DictReader(stream)
                if not reader.fieldnames:
                    raise CommandError('The CSV has no header row.')
                rows = list(reader)
                headers = {normalize_header(name): name for name in reader.fieldnames}
        except UnicodeDecodeError as exc:
            raise CommandError('The file is not UTF-8. Export it as CSV UTF-8.') from exc

        def header(*aliases, contains=None):
            for alias in aliases:
                match = headers.get(normalize_header(alias))
                if match:
                    return match
            if contains:
                for normalized, original in headers.items():
                    if all(token in normalized for token in contains):
                        return original
            return None

        columns = {
            'name': header('1. 姓名', contains=['姓名']),
            'school_short': header('學校簡稱'),
            'email': header('2. 聯絡電子郵件 Email', contains=['聯絡', '電子郵件']),
            'email_fallback': header('電子郵件地址'),
            'note': header('備註'),
            'phone': header('3. 聯絡電話', contains=['電話']),
            'school': header('4. 學校'),
            'student_id': header('5.學號', '5. 學號', contains=['學號']),
            'language': header('7. 預計使用的程式語言', contains=['程式語言']),
        }
        missing = [label for label in ('name', 'phone', 'student_id') if not columns[label]]
        if missing:
            raise CommandError(f'Missing required columns: {", ".join(missing)}')

        parsed = []
        errors = []
        seen = set()
        for row_number, row in enumerate(rows, start=2):
            student_id = (row.get(columns['student_id']) or '').strip()
            phone = normalize_phone(row.get(columns['phone']))
            initial_password = phone or student_id
            name = (row.get(columns['name']) or '').strip()
            if not any((student_id, phone, name)):
                continue
            if not student_id:
                errors.append(f'Row {row_number}: missing student ID')
            elif student_id in seen:
                errors.append(f'Row {row_number}: duplicate student ID {student_id}')
            else:
                seen.add(student_id)
            if phone and (len(phone) < 8 or len(phone) > 15):
                errors.append(f'Row {row_number}: invalid phone for student {student_id or "?"}')
            if not name:
                errors.append(f'Row {row_number}: missing name for student {student_id or "?"}')
            email = ((row.get(columns['email']) if columns['email'] else '') or '').strip()
            if not email and columns['email_fallback']:
                email = (row.get(columns['email_fallback']) or '').strip()
            parsed.append({
                'username': student_id, 'student_id': student_id, 'password': initial_password,
                'first_name': name, 'email': email,
                'school_short_name': ((row.get(columns['school_short']) if columns['school_short'] else '') or '').strip(),
                'school_name': ((row.get(columns['school']) if columns['school'] else '') or '').strip(),
                'preferred_programming_language': ((row.get(columns['language']) if columns['language'] else '') or '').strip(),
                'import_note': ((row.get(columns['note']) if columns['note'] else '') or '').strip(),
            })

        existing = set(User.objects.filter(username__in=seen).values_list('username', flat=True))
        if existing and not options['update_existing']:
            errors.append('Existing accounts: ' + ', '.join(sorted(existing)))
        if errors:
            raise CommandError('\n'.join(errors))

        if options['dry_run']:
            self.stdout.write(self.style.SUCCESS(
                f'Validation passed: {len(parsed)} rows; new={len(parsed) - len(existing)}, '
                f'existing={len(existing)}. No data written.'
            ))
            return

        created = updated = 0
        with transaction.atomic():
            for data in parsed:
                password = data.pop('password')
                user = User.objects.filter(username=data['username']).first()
                if user:
                    for key, value in data.items():
                        setattr(user, key, value)
                    user.role = 'student'
                    if options['reset_passwords']:
                        user.set_password(password)
                        user.must_change_password = True
                    user.save()
                    updated += 1
                else:
                    user = User(**data, role='student', must_change_password=True)
                    user.set_password(password)
                    user.save()
                    created += 1
        self.stdout.write(self.style.SUCCESS(
            f'Import complete: created={created}, updated={updated}. '
            'Phone numbers (or student IDs when phone is blank) were used only to hash '
            'initial passwords and were not stored.'
        ))
