import tempfile
from pathlib import Path

from django.core.management import call_command
from django.test import TestCase
from rest_framework.test import APIClient

from .models import User


CSV_TEXT = """報名順序,1. 姓名,學校簡稱,2. 聯絡電子郵件 Email,備註,3. 聯絡電話,4. 學校,5.學號,7. 預計使用的程式語言,電子郵件地址
1,王小明,測試高中,student@example.com,備註,0912-345-678,測試高級中學,S1234567,Python,
"""


class StudentImportTests(TestCase):
    def make_csv(self):
        handle = tempfile.NamedTemporaryFile(suffix='.csv', delete=False)
        path = Path(handle.name)
        handle.close()
        path.write_text(CSV_TEXT, encoding='utf-8-sig')
        self.addCleanup(path.unlink, missing_ok=True)
        return path

    def test_import_uses_student_id_and_hashed_phone_password(self):
        call_command('import_students', str(self.make_csv()))
        user = User.objects.get(username='S1234567')
        self.assertEqual(user.student_id, 'S1234567')
        self.assertEqual(user.first_name, '王小明')
        self.assertEqual(user.school_short_name, '測試高中')
        self.assertTrue(user.check_password('0912345678'))
        self.assertTrue(user.must_change_password)

    def test_import_uses_student_id_when_phone_is_blank(self):
        csv_text = CSV_TEXT.replace('0912-345-678', '')
        path = self.make_csv()
        path.write_text(csv_text, encoding='utf-8-sig')

        call_command('import_students', str(path))

        user = User.objects.get(username='S1234567')
        self.assertTrue(user.check_password('S1234567'))
        self.assertTrue(user.must_change_password)

    def test_dry_run_does_not_write(self):
        call_command('import_students', str(self.make_csv()), dry_run=True)
        self.assertFalse(User.objects.exists())

    def test_public_registration_endpoint_is_removed(self):
        response = APIClient().post('/api/auth/register/', {}, format='json')
        self.assertEqual(response.status_code, 404)
