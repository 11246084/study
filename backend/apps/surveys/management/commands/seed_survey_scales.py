from django.core.management.base import BaseCommand
from apps.surveys.models import SurveyScale


# 六大構念 + 系統可行性。分數預設李克特 1~5。
# 動機 SIMS 拆四個子構面，並以 group='學習動機' 分組；無動機為「越低越好」。
# 焦慮整體越低越好；系統可行性僅後測。
# 自我學習傾向、批判思考傾向、解決問題傾向為老師新增，題目在紙本問卷上，
# 系統只存構念分數；研究者可在管理後台調整分數範圍或名稱。
SCALES = [
    # key, name, group, higher_is_better, post_only, description
    ('motivation_intrinsic', '內在動機', '學習動機', True, False, 'SIMS 內在動機（題1,5,9,13）'),
    ('motivation_identified', '辨識調節', '學習動機', True, False, 'SIMS 辨識調節（題2,6,10,14）'),
    ('motivation_external', '外在調節', '學習動機', True, False, 'SIMS 外在調節（題3,7,11,15）'),
    ('motivation_amotivation', '無動機', '學習動機', False, False, 'SIMS 無動機，分數越低越好（題4,8,12,16）'),
    ('anxiety', '學習焦慮', '', False, False, '程式設計學習焦慮，分數越低越好（8題）'),
    ('self_directed', '自我學習傾向', '', True, False, '自我導向學習傾向（題目於紙本問卷）'),
    ('critical_thinking', '批判思考傾向', '', True, False, '批判思考傾向（題目於紙本問卷）'),
    ('problem_solving', '解決問題傾向', '', True, False, '問題解決傾向（題目於紙本問卷）'),
    ('feasibility', '系統可行性', '', True, True, 'SUS 系統可行性量表，僅後測（10題）'),
]


class Command(BaseCommand):
    help = '建立/更新問卷構念定義（六大構念 + 系統可行性）。不會刪除已登錄成績。'

    def handle(self, *args, **options):
        created, updated = 0, 0
        for order, (key, name, group, hib, post_only, desc) in enumerate(SCALES, start=1):
            obj, was_created = SurveyScale.objects.update_or_create(
                key=key,
                defaults={
                    'name': name,
                    'group': group,
                    'description': desc,
                    'higher_is_better': hib,
                    'post_only': post_only,
                    'score_min': 1.0,
                    'score_max': 5.0,
                    'order': order,
                    'is_active': True,
                },
            )
            if was_created:
                created += 1
            else:
                updated += 1
        self.stdout.write(self.style.SUCCESS(
            f'問卷構念完成：新增 {created} 筆、更新 {updated} 筆，共 {SurveyScale.objects.count()} 筆。'
        ))
