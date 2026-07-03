import re

from django.conf import settings
from django.test import SimpleTestCase

from .management.commands.curriculum_questions import (
    FILL_BLANK_QUESTIONS,
    QUIZ_QUESTIONS,
    SHORT_ANSWER_QUESTIONS,
)
from .management.commands.seed_data import UNIT_TITLES


class CurriculumStructureTests(SimpleTestCase):
    def test_all_levels_have_eight_units_and_one_hundred_questions(self):
        for bank in (QUIZ_QUESTIONS, SHORT_ANSWER_QUESTIONS, FILL_BLANK_QUESTIONS):
            self.assertEqual(len(bank), 8)
            self.assertTrue(all(len(unit) == 100 for unit in bank))

    def test_question_prompts_are_unique_and_have_no_generation_labels(self):
        for bank in (QUIZ_QUESTIONS, SHORT_ANSWER_QUESTIONS, FILL_BLANK_QUESTIONS):
            for unit in bank:
                prompts = [question['content'] for question in unit]
                self.assertEqual(len(prompts), len(set(prompts)))
                self.assertTrue(all('【變化題' not in prompt for prompt in prompts))

    def test_unit_one_levels_use_distinct_cognitive_operations(self):
        self.assertGreaterEqual(len({q['pattern'] for q in QUIZ_QUESTIONS[0]}), 15)
        self.assertGreaterEqual(len({q['pattern'] for q in SHORT_ANSWER_QUESTIONS[0]}), 15)
        self.assertTrue(all('```python' not in q['content'] for q in QUIZ_QUESTIONS[0]))
        self.assertTrue(all('```python' in q['content'] for q in SHORT_ANSWER_QUESTIONS[0]))

    def test_multiple_choice_has_exactly_one_correct_choice(self):
        for unit in QUIZ_QUESTIONS:
            for question in unit:
                correct_count = sum(is_correct for _, is_correct in question['choices'])
                self.assertEqual(correct_count, 1)

    def test_every_fill_blank_marker_has_matching_answer_line(self):
        for unit in FILL_BLANK_QUESTIONS:
            for question in unit:
                markers = sorted({int(m) for m in re.findall(r'__(\d+)__', question['content'])})
                answer_lines = [line for line in question['correct_answer'].split('\n') if line.strip()]
                self.assertTrue(answer_lines, question['content'][:60])
                self.assertEqual(markers, list(range(1, len(answer_lines) + 1)),
                                 question['content'][:60])

    def test_materials_match_unit_order(self):
        material_dir = settings.BASE_DIR.parent / 'frontend' / 'assets' / 'materials'
        for filename in ('level1.md', 'level2.md', 'level3.md'):
            content = (material_dir / filename).read_text(encoding='utf-8')
            headings = re.findall(r'^## Unit \d+｜(.+)$', content, flags=re.MULTILINE)
            self.assertEqual(headings, UNIT_TITLES)
