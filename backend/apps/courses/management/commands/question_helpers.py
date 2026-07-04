"""題庫共用建構函式（curriculum_questions_v2 與各單元題庫模組共用）。"""


def mc(content, correct, *distractors, explanation=''):
    """選擇題：第一個參數列表位置放正解，seed 時會洗牌。"""
    return {
        'type': 'multiple_choice',
        'content': content,
        'choices': [(correct, True), *[(d, False) for d in distractors]],
        'explanation': explanation or f'正確答案：{correct}',
    }


def fb(content, *answers, explanation=''):
    """程式填空題：內文以 __1__、__2__ 標記空格；list/tuple 代表同格多解。

    全選擇制下會由 curriculum_questions_v2._all_mc() 轉成選擇題。
    """
    lines = []
    for answer in answers:
        if isinstance(answer, (list, tuple)):
            lines.append('|||'.join(answer))
        else:
            lines.append(answer)
    display = '；'.join(f'空格{i}: {line.split("|||")[0]}' for i, line in enumerate(lines, start=1))
    return {
        'type': 'fill_blank',
        'content': content,
        'correct_answer': '\n'.join(lines),
        'explanation': explanation or f'答案 — {display}',
    }
