from django.apps import apps
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError
from django.db.models import Avg, Count, F, Max, Min, Q, ProtectedError
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string
from django.utils.dateparse import parse_datetime
from rest_framework import generics, permissions, response, status, views
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import User
from .serializers import ChangePasswordSerializer, RegisterSerializer, UserProfileSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class LoginView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        resp = super().post(request, *args, **kwargs)
        # 登入成功才累計登入次數（RQ-05 投入度代理變數）
        if resp.status_code == 200:
            username = request.data.get('username')
            if username:
                User.objects.filter(username=username).update(
                    login_count=F('login_count') + 1
                )
        return resp


class SystemStatsView(views.APIView):
    """全站公開統計：整個系統累計登入次數（供各頁 footer 顯示）。"""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        from django.db.models import Sum
        total_logins = User.objects.aggregate(s=Sum('login_count'))['s'] or 0
        return response.Response({'total_logins': total_logins})


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class ChangePasswordView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(status=status.HTTP_204_NO_CONTENT)


class IsManagementUser(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and (user.role == 'admin' or user.is_staff or user.is_superuser)
        )


class StudentUsageView(views.APIView):
    permission_classes = [IsManagementUser]

    def get(self, request):
        from apps.assessments.models import QuizAttempt
        from apps.learning.models import AdaptiveLearningPath, AdaptiveRecommendation

        students = User.objects.filter(role='student').order_by('username')
        attempts_summary = {
            row['student_id']: row
            for row in QuizAttempt.objects.filter(completed_at__isnull=False)
            .values('student_id')
            .annotate(
                attempt_count=Count('id'),
                avg_score=Avg('score'),
                passed_count=Count('id', filter=Q(is_passed=True)),
                completed_units=Count('quiz__lesson__order', distinct=True),
                last_activity=Max('completed_at'),
            )
        }
        latest_paths = {}
        for path in AdaptiveLearningPath.objects.filter(student__role='student').order_by(
            'student_id',
            '-unit_number',
            '-updated_at',
        ):
            latest_paths.setdefault(path.student_id, path)
        active_recommendations = {
            row['student_id']: row['count']
            for row in AdaptiveRecommendation.objects.filter(
                student__role='student',
                is_dismissed=False,
            )
            .values('student_id')
            .annotate(count=Count('id'))
        }

        rows = []
        total_attempts = 0
        total_score_sum = 0
        total_score_count = 0
        active_students = 0
        completed_unit_sum = 0

        for student in students:
            summary = attempts_summary.get(student.id, {})
            attempt_count = summary.get('attempt_count') or 0
            avg_score = summary.get('avg_score')
            passed_count = summary.get('passed_count') or 0
            completed_units = summary.get('completed_units') or 0
            last_activity = summary.get('last_activity')
            pass_rate = round((passed_count / attempt_count) * 100, 1) if attempt_count else None
            latest_path = latest_paths.get(student.id)

            total_attempts += attempt_count
            completed_unit_sum += completed_units
            if avg_score is not None:
                total_score_sum += avg_score
                total_score_count += 1
            if last_activity:
                active_students += 1

            rows.append({
                'id': student.id,
                'username': student.username,
                'email': student.email,
                'student_id': student.student_id,
                'is_active': student.is_active,
                'date_joined': student.date_joined,
                'attempt_count': attempt_count,
                'completed_units': completed_units,
                'avg_score': round(avg_score, 1) if avg_score is not None else None,
                'pass_rate': pass_rate,
                'last_activity': last_activity,
                'current_unit': latest_path.unit_number if latest_path else None,
                'current_level': latest_path.current_level if latest_path else None,
                'active_recommendations': active_recommendations.get(student.id, 0),
            })

        student_count = students.count()
        overview = {
            'student_count': student_count,
            'active_students': active_students,
            'total_attempts': total_attempts,
            'avg_score': round(total_score_sum / total_score_count, 1) if total_score_count else None,
            'avg_completed_units': round(completed_unit_sum / student_count, 1) if student_count else 0,
        }
        return response.Response({'overview': overview, 'students': rows})


def _iso_week(dt):
    year, week, _ = dt.isocalendar()
    return f'{year}-W{week:02d}'


def _survey_scale_rows(agg, single=False):
    """把 (scale_id, phase) → 值 的聚合轉成每構念的前後測比較列。

    agg: dict[(scale_id, phase)] = (value, n)  # 班級用 (平均, 樣本數)
         或單一學生 dict[(scale_id, phase)] = value
    """
    from apps.surveys.models import SurveyScale
    rows = []
    any_data = False
    for s in SurveyScale.objects.filter(is_active=True):
        if single:
            pre_v = agg.get((s.id, 'pre'))
            post_v = agg.get((s.id, 'post'))
            pre_n = post_n = None
        else:
            pre = agg.get((s.id, 'pre'))
            post = agg.get((s.id, 'post'))
            pre_v, pre_n = (round(pre[0], 2), pre[1]) if pre else (None, 0)
            post_v, post_n = (round(post[0], 2), post[1]) if post else (None, 0)
        if pre_v is not None or post_v is not None:
            any_data = True
        delta = round(post_v - pre_v, 2) if (pre_v is not None and post_v is not None) else None
        improved = None
        if delta is not None:
            improved = (delta > 0) if s.higher_is_better else (delta < 0)
        rows.append({
            'key': s.key, 'name': s.name, 'group': s.group,
            'higher_is_better': s.higher_is_better, 'post_only': s.post_only,
            'score_min': s.score_min, 'score_max': s.score_max,
            'pre': pre_v, 'post': post_v, 'pre_n': pre_n, 'post_n': post_n,
            'delta': delta, 'improved': improved,
        })
    return rows, any_data


def _survey_class_summary():
    from django.db.models import Avg, Count
    from apps.surveys.models import SurveyScore
    agg = {}
    for r in (SurveyScore.objects.filter(student__role='student')
              .values('scale_id', 'phase').annotate(a=Avg('score'), n=Count('id'))):
        agg[(r['scale_id'], r['phase'])] = (r['a'], r['n'])
    rows, any_data = _survey_scale_rows(agg, single=False)
    return {
        'status': 'ready' if any_data else 'awaiting',
        'scales': rows,
        'note': '尚未登錄問卷成績；於「問卷成績」登錄前後測分數後即顯示班級前→後測變化。',
    }


def _survey_student_summary(student):
    from apps.surveys.models import SurveyScore
    agg = {
        (sc.scale_id, sc.phase): sc.score
        for sc in SurveyScore.objects.filter(student=student)
    }
    rows, any_data = _survey_scale_rows(agg, single=True)
    return {
        'status': 'ready' if any_data else 'awaiting',
        'scales': rows,
        'note': '尚未登錄此學生的問卷成績。',
    }


def _summarize_sessions(session_values):
    """session_values: iterable of dict(started_at, last_seen[, student_id])。
    回傳每週次數/時長與每次平均時長。"""
    weekly = {}
    seen_student_week = set()
    total_min = 0.0
    n = 0
    for s in session_values:
        n += 1
        mins = max(0.0, (s['last_seen'] - s['started_at']).total_seconds() / 60)
        total_min += mins
        wk = _iso_week(s['started_at'])
        bucket = weekly.setdefault(wk, {'sessions': 0, 'minutes': 0.0})
        bucket['sessions'] += 1
        bucket['minutes'] += mins
        if 'student_id' in s:
            seen_student_week.add((s['student_id'], wk))
    if n == 0:
        return {'status': 'awaiting', 'weekly': [], 'sessions_total': 0,
                'minutes_total': 0, 'avg_session_minutes': None,
                'avg_sessions_per_active_week': None, 'avg_minutes_per_active_week': None,
                'note': '尚無使用時段資料；學生登入並使用系統後開始累積（每 2 分鐘一次心跳）。'}
    weekly_list = [{'week': wk, 'sessions': weekly[wk]['sessions'],
                    'minutes': round(weekly[wk]['minutes'], 1)} for wk in sorted(weekly)]
    # 班級用 (學生,週) 配對為分母；個人用「週」為分母
    pairs = len(seen_student_week) if seen_student_week else len(weekly)
    pairs = pairs or 1
    return {
        'status': 'ready',
        'weekly': weekly_list,
        'sessions_total': n,
        'minutes_total': round(total_min, 1),
        'avg_session_minutes': round(total_min / n, 1),
        'avg_sessions_per_active_week': round(n / pairs, 1),
        'avg_minutes_per_active_week': round(total_min / pairs, 1),
    }


def _usage_class_summary():
    from apps.learning.models import StudySession
    rows = StudySession.objects.filter(student__role='student').values(
        'student_id', 'started_at', 'last_seen')
    return _summarize_sessions(rows)


def _usage_student_summary(student):
    from apps.learning.models import StudySession
    rows = StudySession.objects.filter(student=student).values('started_at', 'last_seen')
    return _summarize_sessions(rows)


def _problem_solving_class_summary(unit_titles):
    """以建構型題目（簡答＋程式）答對率衡量解題能力（RQ：解決問題能力）。
    註：程式題為教師人工複閱、提交即給分，故主指標以簡答題答對率為準。"""
    from django.db.models import Count, Q
    from apps.assessments.models import Answer
    base = Answer.objects.filter(
        attempt__student__role='student',
        question__question_type__in=['short_answer', 'coding'],
    )
    total = base.count()
    if total == 0:
        return {'status': 'awaiting',
                'note': '尚無建構型題目（簡答／程式）作答資料；學生作答後顯示解題能力。'}
    sa = base.filter(question__question_type='short_answer')
    sa_total = sa.count()
    sa_correct = sa.filter(is_correct=True).count()
    coding_total = base.filter(question__question_type='coding').count()
    # 逐單元簡答答對率
    by_unit = []
    for r in (sa.values(unit=F('question__quiz__lesson__order'))
              .annotate(t=Count('id'), c=Count('id', filter=Q(is_correct=True)))
              .order_by('unit')):
        by_unit.append({
            'unit': r['unit'], 'title': unit_titles.get(r['unit'], f"單元 {r['unit']}"),
            'rate': round(r['c'] / r['t'] * 100, 1) if r['t'] else None, 'n': r['t'],
        })
    return {
        'status': 'ready',
        'short_answer_accuracy': round(sa_correct / sa_total * 100, 1) if sa_total else None,
        'short_answer_n': sa_total,
        'coding_submissions': coding_total,
        'by_unit': by_unit,
        'note': '解題能力以建構型題目（簡答＋程式）表現衡量；簡答題為自動比對、程式題為教師複閱。',
    }


def _problem_solving_student_summary(student):
    from django.db.models import Count, Q
    from apps.assessments.models import Answer
    base = Answer.objects.filter(
        attempt__student=student,
        question__question_type__in=['short_answer', 'coding'],
    )
    if base.count() == 0:
        return {'status': 'awaiting', 'note': '尚無建構型題目作答資料。'}
    sa = base.filter(question__question_type='short_answer')
    sa_total = sa.count()
    sa_correct = sa.filter(is_correct=True).count()
    # 班級平均供對照
    class_sa = Answer.objects.filter(
        attempt__student__role='student', question__question_type='short_answer')
    class_total = class_sa.count()
    class_correct = class_sa.filter(is_correct=True).count()
    return {
        'status': 'ready',
        'short_answer_accuracy': round(sa_correct / sa_total * 100, 1) if sa_total else None,
        'short_answer_n': sa_total,
        'coding_submissions': base.filter(question__question_type='coding').count(),
        'class_short_answer_accuracy': round(class_correct / class_total * 100, 1) if class_total else None,
    }


class ResearchAnalyticsView(views.APIView):
    """碩士論文研究分析儀表板資料源。

    GET /api/auth/admin/research-analytics/            → 班級層級
    GET /api/auth/admin/research-analytics/student/<pk>/ → 個人層級

    每個 section 帶 status='ready'|'awaiting' + note，前端據此渲染真實圖或
    「資料累積中」骨架。原則：能算的算真實值、不能算的不編造數字。
    """
    permission_classes = [IsManagementUser]

    UNIT_FALLBACK = ['單元 1', '單元 2', '單元 3', '單元 4', '單元 5', '單元 6', '單元 7', '單元 8']

    def get(self, request, pk=None):
        if pk is not None:
            return self._student_detail(request, pk)
        return self._class_overview(request)

    def _unit_titles(self):
        from apps.courses.models import Lesson
        titles = dict(enumerate(self.UNIT_FALLBACK, start=1))
        for lesson in Lesson.objects.filter(course__difficulty='beginner').order_by('order'):
            if 1 <= lesson.order <= 8:
                titles[lesson.order] = lesson.title
        return titles

    def _class_overview(self, request):
        from collections import Counter
        from django.db.models import Sum
        from apps.assessments.models import QuizAttempt, Answer
        from apps.learning.models import AdaptiveLearningPath, AdaptiveRecommendation, LearningProgress

        students = User.objects.filter(role='student')
        N = students.count()
        unit_titles = self._unit_titles()

        completed_at_qs = QuizAttempt.objects.filter(
            student__role='student', completed_at__isnull=False
        )

        # ── 每生彙整（多處重用） ───────────────────────────────
        avg_score_by_student = {
            r['student_id']: r['a']
            for r in completed_at_qs.values('student_id').annotate(a=Avg('score'))
        }
        units_by_student = {
            r['student_id']: r['u']
            for r in completed_at_qs.values('student_id').annotate(
                u=Count('quiz__lesson__order', distinct=True)
            )
        }
        time_by_student = {
            r['student_id']: r['t'] or 0
            for r in LearningProgress.objects.filter(student__role='student')
            .values('student_id').annotate(t=Sum('time_spent'))
        }

        # ── unit_difficulty（ready）─────────────────────────────
        diff_rows = {
            r['unit']: r for r in Answer.objects.filter(attempt__student__role='student')
            .values(unit=F('question__quiz__lesson__order'))
            .annotate(total=Count('id'), correct=Count('id', filter=Q(is_correct=True)))
        }
        unit_difficulty = []
        for u in range(1, 9):
            row = diff_rows.get(u)
            rate = round(row['correct'] / row['total'] * 100, 1) if row and row['total'] else None
            unit_difficulty.append({
                'unit': u, 'title': unit_titles.get(u, f'單元 {u}'),
                'rate': rate, 'samples': row['total'] if row else 0,
                'alert': rate is not None and rate < 60,
            })
        diff_status = 'ready' if any(r['samples'] for r in unit_difficulty) else 'awaiting'

        # ── misconceptions（ready）──────────────────────────────
        wrong_pairs = Answer.objects.filter(
            is_correct=False, question__question_type='short_answer',
            attempt__student__role='student',
        ).values_list('question__quiz__lesson__order', 'student_answer')
        counter = Counter()
        for order, ans in wrong_pairs:
            text = (ans or '').strip()
            if text:
                counter[(order, text.lower())] += 1
        misconceptions = [
            {'unit': order, 'title': unit_titles.get(order, f'單元 {order}'),
             'text': text, 'count': cnt, 'total': N}
            for (order, text), cnt in counter.most_common(8)
        ]
        misc_status = 'ready' if misconceptions else 'awaiting'

        # ── retake（ready）──────────────────────────────────────
        pairs = {}
        for a in completed_at_qs.order_by('started_at').values(
            'student_id', 'quiz_id', 'score', unit=F('quiz__lesson__order')
        ):
            pairs.setdefault((a['student_id'], a['quiz_id']), []).append(a)
        retake_units = {}
        first_sum = second_sum = n_pairs = 0
        for (sid, qid), lst in pairs.items():
            if len(lst) < 2:
                continue
            n_pairs += 1
            first, second = lst[0], lst[1]
            first_sum += first['score']
            second_sum += second['score']
            ru = retake_units.setdefault(first['unit'], {'first': 0, 'second': 0, 'n': 0})
            ru['first'] += first['score']
            ru['second'] += second['score']
            ru['n'] += 1
        retake = {
            'n_pairs': n_pairs,
            'avg_first': round(first_sum / n_pairs, 1) if n_pairs else None,
            'avg_second': round(second_sum / n_pairs, 1) if n_pairs else None,
            'units': [
                {'unit': u, 'title': unit_titles.get(u, f'單元 {u}'),
                 'first': round(v['first'] / v['n'], 1), 'second': round(v['second'] / v['n'], 1)}
                for u, v in sorted(retake_units.items())
            ],
        }
        retake_status = 'ready' if n_pairs else 'awaiting'

        # ── recommendation_uptake ──────────────────────────────
        recs = AdaptiveRecommendation.objects.filter(student__role='student')
        rec_total = recs.count()
        rec_clicked = recs.filter(is_clicked=True).count()
        rec_ignored = recs.filter(is_dismissed=True, is_clicked=False).count()
        recommendation_uptake = {
            'total': rec_total, 'clicked': rec_clicked, 'ignored': rec_ignored,
            'click_rate': round(rec_clicked / rec_total * 100, 1) if rec_total else None,
        }
        rec_status = 'ready' if rec_clicked else 'awaiting'

        # ── gender（awaiting until filled）──────────────────────
        gender_label = dict(User.GENDER_CHOICES)
        gender_rows = [
            {'gender': r['student__gender'],
             'label': gender_label.get(r['student__gender'], '未填'),
             'avg': round(r['a'], 1) if r['a'] is not None else None,
             'n': r['n']}
            for r in completed_at_qs.exclude(student__gender='')
            .values('student__gender').annotate(a=Avg('score'), n=Count('student_id', distinct=True))
        ]
        gender = {'rows': gender_rows, 'missing': students.filter(gender='').count()}
        gender_status = 'ready' if gender_rows else 'awaiting'

        # ── engagement（awaiting until time accrues）────────────
        engagement_points = [
            {'hours': round(time_by_student.get(sid, 0) / 60, 1),
             'score': round(avg_score_by_student[sid], 1)}
            for sid in avg_score_by_student
            if time_by_student.get(sid, 0) > 0
        ]
        eng_status = 'ready' if engagement_points else 'awaiting'

        # ── risk（ready, 規則式）─────────────────────────────────
        early = {
            r['student_id']: r['a']
            for r in completed_at_qs.filter(quiz__lesson__order__lte=3)
            .values('student_id').annotate(a=Avg('score'))
        }
        risk_high, risk_mid, risk_low = [], [], []
        username_by_id = dict(students.values_list('id', 'username'))
        for sid, avg in early.items():
            entry = {'id': sid, 'username': username_by_id.get(sid), 'score': round(avg, 1)}
            if avg < 60:
                risk_high.append(entry)
            elif avg <= 75:
                risk_mid.append(entry)
            else:
                risk_low.append(entry)
        risk = {
            'high': len(risk_high), 'mid': len(risk_mid), 'low': len(risk_low),
            'high_list': sorted(risk_high, key=lambda x: x['score']),
        }
        risk_status = 'ready' if early else 'awaiting'

        # ── KPI strip ───────────────────────────────────────────
        completion_vals = [units_by_student.get(s, 0) / 8 * 100 for s in username_by_id]
        avg_completion = round(sum(completion_vals) / N, 1) if N else None
        mastery_avg = AdaptiveLearningPath.objects.filter(
            student__role='student'
        ).aggregate(a=Avg('current_level'))['a']
        avg_hours = round(sum(time_by_student.values()) / 60 / N, 1) if N else None

        kpis = [
            {'label': '完成率', 'value': avg_completion, 'unit': '%', 'status': 'ready'},
            {'label': '平均精熟度', 'value': round(mastery_avg, 2) if mastery_avg else None,
             'unit': '/3', 'status': 'ready'},
            {'label': '平均線上時數', 'value': avg_hours, 'unit': 'h',
             'status': 'ready' if avg_hours else 'awaiting', 'note': '埋點累積中'},
            {'label': '推薦點擊率', 'value': recommendation_uptake['click_rate'], 'unit': '%',
             'status': rec_status, 'note': '埋點累積中'},
            {'label': '高風險學生', 'value': risk['high'], 'unit': '人', 'status': risk_status},
            {'label': '已填性別', 'value': N - gender['missing'], 'unit': f'/{N}',
             'status': 'ready' if (N - gender['missing']) else 'awaiting'},
        ]

        period = completed_at_qs.aggregate(start=Min('completed_at'), end=Max('completed_at'))
        return response.Response({
            'meta': {
                'N': N, 'units': 8,
                'period_start': period['start'],
                'period_end': period['end'],
                'students': [{'id': sid, 'username': name} for sid, name in username_by_id.items()],
            },
            'kpis': kpis,
            'unit_difficulty': {'status': diff_status, 'rows': unit_difficulty},
            'misconceptions': {'status': misc_status, 'rows': misconceptions},
            'retake': {'status': retake_status, **retake},
            'recommendation_uptake': {'status': rec_status, **recommendation_uptake},
            'gender': {'status': gender_status, **gender},
            'engagement': {'status': eng_status, 'points': engagement_points},
            'risk': {'status': risk_status, **risk},
            'clustering': {'status': 'awaiting',
                           'note': '需 k-means 分群與足夠樣本數，原料（每生各單元 level）已在累積'},
            'questionnaire': _survey_class_summary(),
            'usage': _usage_class_summary(),
            'problem_solving': _problem_solving_class_summary(unit_titles),
        })

    def _student_detail(self, request, pk):
        from django.db.models import Sum
        from apps.assessments.models import QuizAttempt, Answer
        from apps.learning.models import AdaptiveLearningPath, LearningProgress

        student = get_object_or_404(User, pk=pk, role='student')
        attempts = QuizAttempt.objects.filter(student=student, completed_at__isnull=False)

        completed_units = attempts.values('quiz__lesson__order').distinct().count()
        avg_score = attempts.aggregate(a=Avg('score'))['a']
        hours = (LearningProgress.objects.filter(student=student)
                 .aggregate(t=Sum('time_spent'))['t'] or 0) / 60
        mastery = AdaptiveLearningPath.objects.filter(student=student).aggregate(
            a=Avg('current_level'))['a']

        # 重做次數：同一 quiz 作答 >=2 的份數
        quiz_counts = attempts.values('quiz_id').annotate(c=Count('id'))
        retake_count = sum(1 for r in quiz_counts if r['c'] >= 2)

        # 每單元 level 軌跡
        path_by_unit = {
            p.unit_number: p.current_level
            for p in AdaptiveLearningPath.objects.filter(student=student)
        }
        trajectory = [
            {'unit': u, 'level': path_by_unit.get(u)} for u in range(1, 9)
        ]

        # 個人迷思命中（簡答錯誤）
        wrong = Answer.objects.filter(
            attempt__student=student, is_correct=False,
            question__question_type='short_answer',
        ).values('question__quiz__lesson__order', 'student_answer').distinct()
        # 是否之後在同單元答對 → 視為已重做修正
        correct_units = set(
            Answer.objects.filter(
                attempt__student=student, is_correct=True,
                question__question_type='short_answer',
            ).values_list('question__quiz__lesson__order', flat=True)
        )
        misconception_hits = [
            {'unit': w['question__quiz__lesson__order'],
             'text': (w['student_answer'] or '').strip(),
             'redone': w['question__quiz__lesson__order'] in correct_units}
            for w in wrong if (w['student_answer'] or '').strip()
        ]

        # 班級平均（對照）
        class_avg = QuizAttempt.objects.filter(
            student__role='student', completed_at__isnull=False
        ).aggregate(a=Avg('score'))['a']

        return response.Response({
            'student': {
                'id': student.id, 'username': student.username,
                'student_id': student.student_id,
                'gender': dict(User.GENDER_CHOICES).get(student.gender, ''),
                'date_joined': student.date_joined,
            },
            'metrics': {
                'completed_units': completed_units,
                'mastery': round(mastery, 2) if mastery else None,
                'hours': round(hours, 1),
                'retake_count': retake_count,
            },
            'trajectory': trajectory,
            'misconception_hits': misconception_hits,
            'compare': {
                'score': round(avg_score, 1) if avg_score is not None else None,
                'class_score': round(class_avg, 1) if class_avg is not None else None,
            },
            'questionnaire': _survey_student_summary(student),
            'usage': _usage_student_summary(student),
            'problem_solving': _problem_solving_student_summary(student),
        })


class MyReportView(views.APIView):
    """學生個人成長報表（學生本人可看）。

    刻意不顯示 Level 1/2/3 標籤（學生視角避免標籤化），只呈現：
    六大構念前→後測變化、學習成效（平均分、完成單元）、使用時間、解題能力。
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from django.db.models import Avg, Count
        from apps.assessments.models import QuizAttempt

        student = request.user
        attempts = QuizAttempt.objects.filter(student=student, completed_at__isnull=False)
        avg_score = attempts.aggregate(a=Avg('score'))['a']
        completed_units = attempts.values('quiz__lesson__order').distinct().count()
        class_avg = QuizAttempt.objects.filter(
            student__role='student', completed_at__isnull=False
        ).aggregate(a=Avg('score'))['a']

        return response.Response({
            'student': {'username': student.username},
            'effectiveness': {
                'avg_score': round(avg_score, 1) if avg_score is not None else None,
                'completed_units': completed_units,
                'total_units': 8,
                'class_avg_score': round(class_avg, 1) if class_avg is not None else None,
            },
            'questionnaire': _survey_student_summary(student),
            'usage': _usage_student_summary(student),
            'problem_solving': _problem_solving_student_summary(student),
        })


def _display_value(obj, field_name):
    value = getattr(obj, field_name)
    if hasattr(value, 'pk'):
        return {'id': value.pk, 'label': str(value)}
    return value


def _coerce_value(field, value):
    if value in ('', None):
        if getattr(field, 'null', False):
            return None
        return ''
    field_type = field.get_internal_type()
    if field_type in ('IntegerField', 'PositiveIntegerField', 'BigAutoField'):
        return int(value)
    if field_type == 'FloatField':
        return float(value)
    if field_type == 'BooleanField':
        return value in (True, 'true', 'True', '1', 1, 'on', 'yes')
    if field_type == 'DateTimeField':
        return parse_datetime(value) if isinstance(value, str) else value
    return value


class AdminDataView(views.APIView):
    permission_classes = [IsManagementUser]

    CONFIG = {
        'users': {
            'model': ('users', 'User'),
            'title': '使用者',
            'search': ['username', 'email', 'student_id'],
            'order': ['role', 'username'],
            'columns': ['id', 'username', 'email', 'role', 'student_id', 'gender', 'is_active', 'date_joined'],
            'editable': ['email', 'role', 'student_id', 'gender', 'is_active'],
            'create': ['username', 'email', 'password', 'role', 'student_id', 'gender', 'is_active'],
            'filters': {'role': ['student', 'teacher', 'admin'], 'is_active': [True, False]},
        },
        'courses': {
            'model': ('courses', 'Course'),
            'title': '課程',
            'search': ['title', 'description', 'teacher__username'],
            'order': ['id'],
            'columns': ['id', 'title', 'teacher', 'difficulty', 'is_active', 'created_at'],
            'editable': ['title', 'description', 'teacher', 'difficulty', 'is_active'],
            'create': ['title', 'description', 'teacher', 'difficulty', 'is_active'],
            'filters': {'difficulty': ['beginner', 'intermediate', 'advanced'], 'is_active': [True, False]},
        },
        'lessons': {
            'model': ('courses', 'Lesson'),
            'title': '單元',
            'search': ['title', 'course__title', 'content'],
            'order': ['course__id', 'order'],
            'columns': ['id', 'course', 'title', 'lesson_type', 'order', 'duration_minutes'],
            'editable': ['course', 'title', 'content', 'lesson_type', 'order', 'duration_minutes'],
            'create': ['course', 'title', 'content', 'lesson_type', 'order', 'duration_minutes'],
            'filters': {'lesson_type': ['text', 'video', 'exercise']},
        },
        'enrollments': {
            'model': ('courses', 'Enrollment'),
            'title': '選課紀錄',
            'search': ['student__username', 'course__title'],
            'order': ['-enrolled_at'],
            'columns': ['id', 'student', 'course', 'progress', 'enrolled_at'],
            'editable': ['student', 'course', 'progress'],
            'create': ['student', 'course', 'progress'],
            'filters': {},
        },
        'quizzes': {
            'model': ('assessments', 'Quiz'),
            'title': '評量',
            'search': ['title', 'lesson__title'],
            'order': ['lesson__course__id', 'lesson__order'],
            'columns': ['id', 'title', 'lesson', 'quiz_type', 'pass_score', 'created_at'],
            'editable': ['lesson', 'title', 'quiz_type', 'pass_score'],
            'create': ['lesson', 'title', 'quiz_type', 'pass_score'],
            'filters': {'quiz_type': ['formative', 'summative']},
        },
        'questions': {
            'model': ('assessments', 'Question'),
            'title': '題目',
            'search': ['content', 'quiz__title'],
            'order': ['quiz__lesson__course__id', 'quiz__lesson__order', 'order'],
            'columns': ['id', 'quiz', 'order', 'question_type', 'content', 'points'],
            'editable': ['quiz', 'order', 'question_type', 'content', 'correct_answer', 'points', 'explanation'],
            'create': ['quiz', 'order', 'question_type', 'content', 'correct_answer', 'points', 'explanation'],
            'filters': {'question_type': ['multiple_choice', 'true_false', 'short_answer', 'coding']},
        },
        'attempts': {
            'model': ('assessments', 'QuizAttempt'),
            'title': '作答紀錄',
            'search': ['student__username', 'quiz__title', 'quiz__lesson__title'],
            'order': ['-started_at'],
            'columns': ['id', 'student', 'quiz', 'score', 'is_passed', 'started_at', 'completed_at'],
            'editable': ['student', 'quiz', 'score', 'is_passed', 'completed_at'],
            'create': ['student', 'quiz', 'score', 'is_passed', 'completed_at'],
            'filters': {'is_passed': [True, False]},
        },
        'adaptive': {
            'model': ('learning', 'AdaptiveLearningPath'),
            'title': '適性路徑',
            'search': ['student__username'],
            'order': ['student__username', 'unit_number'],
            'columns': ['id', 'student', 'unit_number', 'current_level', 'last_score', 'updated_at'],
            'editable': ['student', 'unit_number', 'current_level', 'last_score'],
            'create': ['student', 'unit_number', 'current_level', 'last_score'],
            'filters': {'current_level': [1, 2, 3]},
        },
        'recommendations': {
            'model': ('learning', 'AdaptiveRecommendation'),
            'title': '推薦紀錄',
            'search': ['student__username', 'recommended_lesson__title', 'reason'],
            'order': ['-created_at'],
            'columns': ['id', 'student', 'recommended_lesson', 'reason', 'is_dismissed', 'created_at'],
            'editable': ['student', 'recommended_lesson', 'reason', 'is_dismissed'],
            'create': ['student', 'recommended_lesson', 'reason', 'is_dismissed'],
            'filters': {'is_dismissed': [True, False]},
        },
        'progress': {
            'model': ('learning', 'LearningProgress'),
            'title': '學習進度',
            'search': ['student__username', 'lesson__title'],
            'order': ['-last_accessed'],
            'columns': ['id', 'student', 'lesson', 'status', 'time_spent', 'last_accessed', 'completed_at'],
            'editable': ['student', 'lesson', 'status', 'time_spent', 'completed_at'],
            'create': ['student', 'lesson', 'status', 'time_spent', 'completed_at'],
            'filters': {'status': ['not_started', 'in_progress', 'completed']},
        },
        'performance': {
            'model': ('learning', 'PerformanceRecord'),
            'title': '學習表現',
            'search': ['student__username', 'course__title'],
            'order': ['course__title'],
            'columns': ['id', 'student', 'course', 'quiz_score_avg', 'proficiency', 'recorded_at'],
            'editable': ['student', 'course', 'quiz_score_avg', 'proficiency'],
            'create': ['student', 'course', 'quiz_score_avg', 'proficiency'],
            'filters': {'proficiency': ['low', 'medium', 'high']},
        },
        'survey_scales': {
            'model': ('surveys', 'SurveyScale'),
            'title': '問卷構念',
            'search': ['name', 'key', 'group'],
            'order': ['order', 'id'],
            'columns': ['id', 'order', 'name', 'group', 'key', 'higher_is_better', 'post_only', 'is_active'],
            'editable': ['order', 'name', 'group', 'description', 'score_min', 'score_max', 'higher_is_better', 'post_only', 'is_active'],
            'create': ['key', 'order', 'name', 'group', 'description', 'score_min', 'score_max', 'higher_is_better', 'post_only', 'is_active'],
            'filters': {'higher_is_better': [True, False], 'post_only': [True, False], 'is_active': [True, False]},
        },
        'survey_scores': {
            'model': ('surveys', 'SurveyScore'),
            'title': '問卷成績',
            'search': ['student__username', 'scale__name'],
            'order': ['scale__order', 'phase', 'student__username'],
            'columns': ['id', 'student', 'scale', 'phase', 'score', 'recorded_at'],
            'editable': ['student', 'scale', 'phase', 'score', 'note'],
            'create': ['student', 'scale', 'phase', 'score', 'note'],
            'filters': {'phase': ['pre', 'post']},
        },
    }

    def get_config(self, key):
        config = self.CONFIG.get(key)
        if not config:
            return None, None
        return config, apps.get_model(*config['model'])

    def get_queryset(self, request, config, model):
        qs = model.objects.all()
        search = request.GET.get('search', '').strip()
        if search:
            query = Q()
            for field in config['search']:
                query |= Q(**{f'{field}__icontains': search})
            qs = qs.filter(query)
        for name, choices in config['filters'].items():
            raw = request.GET.get(name)
            if raw not in (None, ''):
                field = model._meta.get_field(name)
                qs = qs.filter(**{name: _coerce_value(field, raw)})
        return qs.order_by(*config['order'])

    def field_schema(self, model, name, include_password=False):
        if name == 'password':
            return {'name': name, 'type': 'password', 'label': 'password', 'editable': True}
        field = model._meta.get_field(name)
        schema = {
            'name': name,
            'type': field.get_internal_type(),
            'label': field.verbose_name or name,
            'editable': True,
            'required': not getattr(field, 'blank', False) and not getattr(field, 'null', False),
        }
        if getattr(field, 'choices', None):
            schema['choices'] = [{'value': value, 'label': label} for value, label in field.choices]
        if field.many_to_one:
            related = field.remote_field.model
            schema['type'] = 'ForeignKey'
            schema['options'] = [
                {'value': obj.pk, 'label': str(obj)}
                for obj in related.objects.all()[:200]
            ]
        return schema

    def serialize(self, obj, config):
        data = {'id': obj.pk}
        for field in config['columns']:
            data[field] = _display_value(obj, field)
        return data

    def get(self, request, key):
        config, model = self.get_config(key)
        if not config:
            return response.Response({'detail': 'Unknown data model.'}, status=status.HTTP_404_NOT_FOUND)
        qs = self.get_queryset(request, config, model)
        try:
            page_size = max(1, min(int(request.GET.get('page_size', 25)), 100))
            page = max(int(request.GET.get('page', 1)), 1)
        except (TypeError, ValueError):
            return response.Response({'detail': 'Invalid pagination values.'}, status=status.HTTP_400_BAD_REQUEST)
        start = (page - 1) * page_size
        rows = qs[start:start + page_size]
        return response.Response({
            'key': key,
            'title': config['title'],
            'count': qs.count(),
            'page': page,
            'page_size': page_size,
            'columns': [self.field_schema(model, name) for name in config['columns']],
            'editable_fields': [self.field_schema(model, name, include_password=True) for name in config['editable']],
            'create_fields': [self.field_schema(model, name, include_password=True) for name in config['create']],
            'filters': config['filters'],
            'results': [self.serialize(obj, config) for obj in rows],
        })

    def post(self, request, key):
        config, model = self.get_config(key)
        if not config:
            return response.Response({'detail': 'Unknown data model.'}, status=status.HTTP_404_NOT_FOUND)
        data = request.data.copy()
        if key == 'users':
            password = data.pop('password', None) or get_random_string(16)
            username = data.pop('username', None)
            if not username:
                return response.Response({'detail': 'username is required.'}, status=status.HTTP_400_BAD_REQUEST)
            obj = User(username=username, **{k: data[k] for k in data if k in config['editable']})
            obj.set_password(password)
            try:
                obj.full_clean()
                obj.save()
            except (DjangoValidationError, IntegrityError, TypeError, ValueError) as exc:
                detail = getattr(exc, 'message_dict', None) or str(exc)
                return response.Response({'detail': detail}, status=status.HTTP_400_BAD_REQUEST)
            return response.Response(self.serialize(obj, config), status=status.HTTP_201_CREATED)

        obj = model()
        for name in config['create']:
            if name not in data:
                continue
            field = model._meta.get_field(name)
            value = data[name]
            if field.many_to_one:
                setattr(obj, f'{name}_id', value or None)
            else:
                setattr(obj, name, _coerce_value(field, value))
        try:
            obj.full_clean()
            obj.save()
        except (DjangoValidationError, IntegrityError, TypeError, ValueError) as exc:
            detail = getattr(exc, 'message_dict', None) or str(exc)
            return response.Response({'detail': detail}, status=status.HTTP_400_BAD_REQUEST)
        return response.Response(self.serialize(obj, config), status=status.HTTP_201_CREATED)

    def patch(self, request, key, pk):
        config, model = self.get_config(key)
        if not config:
            return response.Response({'detail': 'Unknown data model.'}, status=status.HTTP_404_NOT_FOUND)
        obj = get_object_or_404(model, pk=pk)
        for name in config['editable']:
            if name not in request.data:
                continue
            field = model._meta.get_field(name)
            value = request.data[name]
            if field.many_to_one:
                setattr(obj, f'{name}_id', value or None)
            else:
                setattr(obj, name, _coerce_value(field, value))
        try:
            obj.full_clean()
            obj.save()
        except (DjangoValidationError, IntegrityError, TypeError, ValueError) as exc:
            detail = getattr(exc, 'message_dict', None) or str(exc)
            return response.Response({'detail': detail}, status=status.HTTP_400_BAD_REQUEST)
        return response.Response(self.serialize(obj, config))

    # 學生作答／學習歷程屬研究資料，受保護不開放從資料管理直接刪除
    PROTECTED_STUDENT_DATA = {'attempts', 'progress', 'recommendations', 'adaptive', 'performance', 'enrollments'}

    def delete(self, request, key, pk):
        config, model = self.get_config(key)
        if not config:
            return response.Response({'detail': 'Unknown data model.'}, status=status.HTTP_404_NOT_FOUND)
        if key in self.PROTECTED_STUDENT_DATA:
            return response.Response(
                {'detail': f'「{config["title"]}」屬學生學習歷程資料，受保護不開放刪除，以免影響研究分析。'},
                status=status.HTTP_409_CONFLICT,
            )
        obj = get_object_or_404(model, pk=pk)
        try:
            obj.delete()
        except ProtectedError as exc:
            protected = {str(o) for o in exc.protected_objects}
            sample = '、'.join(list(protected)[:5])
            return response.Response(
                {'detail': f'無法刪除：尚有 {len(protected)} 筆關聯資料指向此項目（例如 {sample}）。'
                           f'請先重新指派或刪除這些關聯資料。'},
                status=status.HTTP_409_CONFLICT,
            )
        return response.Response(status=status.HTTP_204_NO_CONTENT)
