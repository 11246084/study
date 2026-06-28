from rest_framework.test import APITestCase

from apps.users.models import User
from .models import SurveyScale, SurveyScore


class SurveyValidationTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin', password='password123', role='admin', is_staff=True,
        )
        self.student = User.objects.create_user(username='student', password='password123')
        self.scale = SurveyScale.objects.create(
            key='motivation', name='Motivation', score_min=1, score_max=5,
        )
        self.client.force_authenticate(self.admin)

    def test_batch_rejects_score_outside_scale(self):
        response = self.client.post('/api/surveys/scores/batch/', {
            'scale': self.scale.key,
            'phase': 'pre',
            'scores': {str(self.student.id): 8},
        }, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['saved'], 0)
        self.assertEqual(len(response.data['errors']), 1)
        self.assertFalse(SurveyScore.objects.exists())

    def test_post_only_scale_rejects_pre_score(self):
        self.scale.post_only = True
        self.scale.save()
        response = self.client.post('/api/surveys/scores/batch/', {
            'scale': self.scale.key,
            'phase': 'pre',
            'scores': {str(self.student.id): 3},
        }, format='json')

        self.assertEqual(response.data['saved'], 0)
        self.assertIn('僅允許後測', response.data['errors'][0]['detail'])

    def test_csv_reports_invalid_cells(self):
        csv_text = f'username,{self.scale.key}_pre\n{self.student.username},99\n'
        response = self.client.post('/api/surveys/scores/import/', {'csv': csv_text}, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['saved'], 0)
        self.assertEqual(len(response.data['errors']), 1)

