import re

from django.conf import settings
from django.test import SimpleTestCase

from .management.commands.curriculum_questions import (
    CODING_QUESTIONS,
    QUIZ_QUESTIONS,
    SHORT_ANSWER_QUESTIONS,
)
from .management.commands.seed_data import UNIT_TITLES


class CurriculumStructureTests(SimpleTestCase):
    def test_all_levels_have_eight_units_and_ten_questions(self):
        for bank in (QUIZ_QUESTIONS, SHORT_ANSWER_QUESTIONS, CODING_QUESTIONS):
            self.assertEqual(len(bank), 8)
            self.assertTrue(all(len(unit) == 10 for unit in bank))

    def test_multiple_choice_has_exactly_one_correct_choice(self):
        for unit in QUIZ_QUESTIONS:
            for question in unit:
                correct_count = sum(is_correct for _, is_correct in question['choices'])
                self.assertEqual(correct_count, 1)

    def test_every_coding_question_has_an_accepted_answer(self):
        for unit in CODING_QUESTIONS:
            for question in unit:
                self.assertTrue(question['correct_answer'].strip())

    def test_materials_match_unit_order(self):
        material_dir = settings.BASE_DIR.parent / 'frontend' / 'assets' / 'materials'
        for filename in ('level1.md', 'level2.md', 'level3.md'):
            content = (material_dir / filename).read_text(encoding='utf-8')
            headings = re.findall(r'^## Unit \d+｜(.+)$', content, flags=re.MULTILINE)
            self.assertEqual(headings, UNIT_TITLES)
