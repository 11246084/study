from django.apps import apps
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError
from django.db.models import Avg, Count, F, Max, Min, Q, ProtectedError
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from datetime import timedelta
import json
from rest_framework import generics, permissions, response, status, views
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import User, LoginEvent
from .serializers import ChangePasswordSerializer, UserProfileSerializer


class LoginView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        resp = super().post(request, *args, **kwargs)
        username = str(request.data.get('username') or '')[:150]
        forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '')
        ip_address = (forwarded.split(',')[0].strip() if forwarded else request.META.get('REMOTE_ADDR')) or None
        event_kwargs = {
            'username_attempt': username,
            'event_type': 'login_success' if resp.status_code == 200 else 'login_failed',
            'ip_address': ip_address,
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
        }
        # 登入成功才累計登入次數（RQ-05 投入度代理變數）
        if resp.status_code == 200:
            if username:
                User.objects.filter(username=username).update(
                    login_count=F('login_count') + 1
                )
                event_kwargs['user'] = User.objects.filter(username=username).first()
        LoginEvent.objects.create(**event_kwargs)
        return resp


class LogoutView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '')
        ip_address = (forwarded.split(',')[0].strip() if forwarded else request.META.get('REMOTE_ADDR')) or None
        LoginEvent.objects.create(
            user=request.user, username_attempt=request.user.username,
            event_type='logout', ip_address=ip_address,
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
        )
        from apps.learning.models import StudySession, StudentEvent
        now = timezone.now()
        session = StudySession.objects.filter(
            student=request.user, ended_at__isnull=True,
        ).order_by('-last_seen').first()
        if session:
            session.ended_at = now
            session.end_reason = 'logout'
            session.save(update_fields=['ended_at', 'end_reason'])
            StudentEvent.objects.create(
                student=request.user, session=session, event_type='session_end',
                metadata={'reason': 'logout'},
            )
        return response.Response(status=status.HTTP_204_NO_CONTENT)


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


def _summarize_sessions(session_values):
    """session_values: iterable of dict(started_at, last_seen[, student_id])。
    回傳每週次數/時長、最近活動週的每日時長與每次平均時長。"""
    weekly = {}
    daily_minutes = {}
    seen_student_week = set()
    total_min = 0.0
    n = 0
    for s in session_values:
        n += 1
        mins = max(0.0, (s['last_seen'] - s['started_at']).total_seconds() / 60)
        total_min += mins
        # USE_TZ=False 時資料庫回傳本地 naive datetime；若未來改成 aware
        # datetime，才需要轉換到專案時區。
        local_started = (timezone.localtime(s['started_at'])
                         if timezone.is_aware(s['started_at']) else s['started_at'])
        wk = _iso_week(local_started)
        bucket = weekly.setdefault(wk, {'sessions': 0, 'minutes': 0.0})
        bucket['sessions'] += 1
        bucket['minutes'] += mins
        day = local_started.date()
        daily_minutes[day] = daily_minutes.get(day, 0.0) + mins
        if 'student_id' in s:
            seen_student_week.add((s['student_id'], wk))
    if n == 0:
        return {'status': 'awaiting', 'weekly': [], 'daily': [], 'sessions_total': 0,
                'minutes_total': 0, 'avg_session_minutes': None,
                'avg_sessions_per_active_week': None, 'avg_minutes_per_active_week': None,
                'note': '尚無使用時段資料；學生登入並使用系統後開始累積（每 2 分鐘一次心跳）。'}
    weekly_list = [{'week': wk, 'sessions': weekly[wk]['sessions'],
                    'minutes': round(weekly[wk]['minutes'], 1)} for wk in sorted(weekly)]
    latest_day = max(daily_minutes)
    week_start = latest_day - timedelta(days=latest_day.weekday())
    daily_list = [
        {'date': (week_start + timedelta(days=i)).isoformat(),
         'minutes': round(daily_minutes.get(week_start + timedelta(days=i), 0.0), 1)}
        for i in range(7)
    ]
    # 班級用 (學生,週) 配對為分母；個人用「週」為分母
    pairs = len(seen_student_week) if seen_student_week else len(weekly)
    pairs = pairs or 1
    return {
        'status': 'ready',
        'weekly': weekly_list,
        'daily': daily_list,
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
        from apps.assessments.models import QuizAttempt, Answer
        from apps.learning.models import (AdaptiveLearningPath, AdaptiveRecommendation,
                                          StudentEvent, StudySession)

        students = User.objects.filter(role='student')
        N = students.count()
        unit_titles = self._unit_titles()
        username_by_id = dict(students.values_list('id', 'username'))

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
        # 線上時數統一以 StudySession 心跳時段計（與「使用時間」卡同一定義）
        time_by_student = {}  # student_id -> 分鐘
        for s in StudySession.objects.filter(student__role='student').values(
                'student_id', 'started_at', 'last_seen'):
            mins = max(0.0, (s['last_seen'] - s['started_at']).total_seconds() / 60)
            time_by_student[s['student_id']] = time_by_student.get(s['student_id'], 0.0) + mins

        # ── unit_difficulty：每位學生每單元只採第一次完成作答 ──
        # 重做資料留給 retake 分析，避免重做次數多的學生在瓶頸圖被重複加權。
        first_attempt_ids = []
        seen_student_units = set()
        for attempt in completed_at_qs.values(
                'id', 'student_id', unit=F('quiz__lesson__order')).order_by(
                    'student_id', 'quiz__lesson__order', 'completed_at', 'id'):
            key = (attempt['student_id'], attempt['unit'])
            if attempt['unit'] is not None and key not in seen_student_units:
                seen_student_units.add(key)
                first_attempt_ids.append(attempt['id'])
        diff_rows = {
            r['unit']: r for r in Answer.objects.filter(attempt_id__in=first_attempt_ids)
            .values(unit=F('question__quiz__lesson__order'))
            .annotate(total=Count('id'), correct=Count('id', filter=Q(is_correct=True)),
                      students=Count('attempt__student_id', distinct=True))
        }
        unit_difficulty = []
        for u in range(1, 9):
            row = diff_rows.get(u)
            rate = round(row['correct'] / row['total'] * 100, 1) if row and row['total'] else None
            unit_difficulty.append({
                'unit': u, 'title': unit_titles.get(u, f'單元 {u}'),
                'rate': rate, 'samples': row['total'] if row else 0,
                'students': row['students'] if row else 0,
                'alert': rate is not None and rate < 60,
            })
        diff_status = 'ready' if any(r['samples'] for r in unit_difficulty) else 'awaiting'

        # ── misconceptions：三等級（選擇誘答／簡答錯誤／填空逐格）──
        # 分子＝犯該錯誤的不重複人數；分母＝該單元作答過該題型的不重複人數
        from apps.assessments.models import Choice
        from apps.assessments.views import fill_blank_config, normalize_blank_answer

        answered = {}   # (unit, qtype) -> set(student_id)
        errors = {}     # (unit, qtype, text) -> set(student_id)
        mc_wrong = []   # (unit, student_id, choice_id)

        con_rows = Answer.objects.filter(
            attempt__student__role='student',
            question__question_type__in=['multiple_choice', 'short_answer', 'fill_blank'],
        ).values(
            'student_answer', 'is_correct',
            sid=F('attempt__student_id'),
            unit=F('question__quiz__lesson__order'),
            qtype=F('question__question_type'),
            answer_key=F('question__correct_answer'),
        )
        for row in con_rows:
            answered.setdefault((row['unit'], row['qtype']), set()).add(row['sid'])
            if row['is_correct']:
                continue
            if row['qtype'] == 'multiple_choice':
                try:
                    mc_wrong.append((row['unit'], row['sid'], int(row['student_answer'])))
                except (TypeError, ValueError):
                    pass
            elif row['qtype'] == 'short_answer':
                text = (row['student_answer'] or '').strip()
                if text:
                    errors.setdefault((row['unit'], 'short_answer', text.lower()), set()).add(row['sid'])
            else:  # fill_blank：逐格比對，收集答錯格的實際填答
                blanks = fill_blank_config(row['answer_key'])
                submitted = (row['student_answer'] or '').replace('\r\n', '\n').replace('\r', '\n').split('\n')
                for i, alternatives in enumerate(blanks):
                    value = submitted[i] if i < len(submitted) else ''
                    if normalize_blank_answer(value) in {normalize_blank_answer(a) for a in alternatives}:
                        continue
                    text = value.strip() or '（未填）'
                    errors.setdefault((row['unit'], 'fill_blank', text), set()).add(row['sid'])

        choice_map = Choice.objects.in_bulk({cid for _, _, cid in mc_wrong})
        for unit, sid, cid in mc_wrong:
            choice = choice_map.get(cid)
            if choice:
                errors.setdefault(
                    (unit, 'multiple_choice', choice.content.strip()), set()).add(sid)

        ranked = sorted(errors.items(), key=lambda kv: -len(kv[1]))[:10]
        misconceptions = [
            {'unit': unit, 'title': unit_titles.get(unit, f'單元 {unit}'),
             'qtype': qtype, 'text': text, 'count': len(sids),
             'total': len(answered.get((unit, qtype), ())) or N}
            for (unit, qtype, text), sids in ranked
        ]
        misc_status = 'ready' if misconceptions else 'awaiting'

        # ── retake（ready）──────────────────────────────────────
        pairs = {}
        for a in completed_at_qs.order_by('started_at').values(
            'student_id', 'quiz_id', 'score', unit=F('quiz__lesson__order')
        ):
            pairs.setdefault((a['student_id'], a['quiz_id']), []).append(a)
        retake_units = {}
        retake_details = []
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
            delta = second['score'] - first['score']
            retake_details.append({
                'student_id': sid,
                'username': username_by_id.get(sid, str(sid)),
                'unit': first['unit'],
                'title': unit_titles.get(first['unit'], f"單元 {first['unit']}"),
                'first': round(first['score'], 1),
                'second': round(second['score'], 1),
                'delta': round(delta, 1),
            })
        retake_details.sort(key=lambda row: (row['username'], row['unit']))
        retake = {
            'n_pairs': n_pairs,
            'avg_first': round(first_sum / n_pairs, 1) if n_pairs else None,
            'avg_second': round(second_sum / n_pairs, 1) if n_pairs else None,
            'details': retake_details,
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
        rec_clicked = recs.filter(click_count__gt=0).count()
        rec_ignored = recs.filter(is_dismissed=True, click_count=0).count()
        recommendation_uptake = {
            'total': rec_total, 'clicked': rec_clicked, 'ignored': rec_ignored,
            'click_rate': round(rec_clicked / rec_total * 100, 1) if rec_total else None,
        }
        rec_status = 'ready' if rec_clicked else 'awaiting'

        # ── engagement：使用時間排名 + 班級單元分數分布 ────────
        usage_ranking = sorted([
            {'student_id': sid, 'username': username_by_id.get(sid, str(sid)),
             'minutes': round(minutes, 1)}
            for sid, minutes in time_by_student.items() if minutes > 0
        ], key=lambda row: (-row['minutes'], row['username']))

        score_by_student = {}
        for row in completed_at_qs.values(
                'student_id', unit=F('quiz__lesson__order')).annotate(avg=Avg('score')):
            if row['unit'] is not None and 1 <= row['unit'] <= 8:
                score_by_student.setdefault(row['student_id'], {})[row['unit']] = round(row['avg'], 1)
        def percentile(values, ratio):
            if not values:
                return None
            ordered = sorted(values)
            pos = (len(ordered) - 1) * ratio
            lower = int(pos)
            upper = min(lower + 1, len(ordered) - 1)
            weight = pos - lower
            return ordered[lower] * (1 - weight) + ordered[upper] * weight

        score_summary = []
        for unit in range(1, 9):
            values = [scores[unit] for scores in score_by_student.values() if unit in scores]
            score_summary.append({
                'unit': unit,
                'avg': round(sum(values) / len(values), 1) if values else None,
                'q1': round(percentile(values, .25), 1) if values else None,
                'q3': round(percentile(values, .75), 1) if values else None,
                'n': len(values),
            })
        score_ready = any(row['n'] for row in score_summary)
        eng_status = 'ready' if usage_ranking or score_ready else 'awaiting'

        # ── attempt_effort：作答時長與放棄率 ─────────────────────
        eff = {u: {'mins': 0.0, 'n_mins': 0, 'completed': 0, 'abandoned': 0}
               for u in range(1, 9)}
        for a in QuizAttempt.objects.filter(student__role='student').values(
                'started_at', 'completed_at', 'abandoned_at', unit=F('quiz__lesson__order')):
            u = a['unit']
            if u not in eff:
                continue
            if a['completed_at']:
                eff[u]['completed'] += 1
                mins = (a['completed_at'] - a['started_at']).total_seconds() / 60
                if 0 < mins <= 180:  # 排除掛機造成的異常時長
                    eff[u]['mins'] += mins
                    eff[u]['n_mins'] += 1
            elif a['abandoned_at']:
                eff[u]['abandoned'] += 1
        effort_rows = []
        for u in range(1, 9):
            e = eff[u]
            finished = e['completed'] + e['abandoned']
            effort_rows.append({
                'unit': u, 'title': unit_titles.get(u, f'單元 {u}'),
                'avg_minutes': round(e['mins'] / e['n_mins'], 1) if e['n_mins'] else None,
                'abandon_rate': round(e['abandoned'] / finished * 100, 1) if finished else None,
                'completed': e['completed'], 'abandoned': e['abandoned'],
            })
        attempt_effort = {
            'status': 'ready' if any(r['completed'] or r['abandoned'] for r in effort_rows)
                      else 'awaiting',
            'rows': effort_rows,
        }

        # ── level_flow：各單元等級分布＋升降統計（適性分流證據）──
        paths = list(AdaptiveLearningPath.objects.filter(student__role='student')
                     .values('student_id', 'unit_number', 'current_level'))
        level_dist = {u: {1: 0, 2: 0, 3: 0} for u in range(1, 9)}
        levels_by_student = {}
        for p in paths:
            if 1 <= p['unit_number'] <= 8 and p['current_level'] in (1, 2, 3):
                level_dist[p['unit_number']][p['current_level']] += 1
                levels_by_student.setdefault(p['student_id'], {})[p['unit_number']] = p['current_level']
        lv_up = lv_down = lv_same = 0
        for levels in levels_by_student.values():
            for u in range(1, 8):
                if u in levels and (u + 1) in levels:
                    if levels[u + 1] > levels[u]:
                        lv_up += 1
                    elif levels[u + 1] < levels[u]:
                        lv_down += 1
                    else:
                        lv_same += 1
        level_flow = {
            'status': 'ready' if paths else 'awaiting',
            'dist': [{'unit': u, 'title': unit_titles.get(u, f'單元 {u}'),
                      'l1': level_dist[u][1], 'l2': level_dist[u][2], 'l3': level_dist[u][3]}
                     for u in range(1, 9)],
            'up': lv_up, 'down': lv_down, 'same': lv_same,
            'note': '尚無適性路徑資料；學生交卷後系統會為下一單元指定等級，此圖自動累積。',
        }

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
            {'label': '樣本數', 'value': N, 'unit': '人', 'status': 'ready'},
        ]

        period = completed_at_qs.aggregate(start=Min('completed_at'), end=Max('completed_at'))
        event_rows = list(
            StudentEvent.objects.filter(student__role='student')
            .values('event_type').annotate(count=Count('id')).order_by('-count')[:20]
        )
        event_total = sum(row['count'] for row in event_rows)
        event_analytics = {
            'status': 'ready' if event_total else 'awaiting',
            'total': event_total,
            'by_type': event_rows,
            'students': StudentEvent.objects.values('student_id').distinct().count(),
        }
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
            'engagement': {
                'status': eng_status,
                'usage_status': 'ready' if usage_ranking else 'awaiting',
                'score_status': 'ready' if score_ready else 'awaiting',
                'usage_ranking': usage_ranking,
                'score_summary': score_summary,
            },
            'level_flow': level_flow,
            'attempt_effort': attempt_effort,
            'usage': _usage_class_summary(),
            'event_analytics': event_analytics,
        })

    def _student_detail(self, request, pk):
        from apps.assessments.models import QuizAttempt, Answer
        from apps.learning.models import AdaptiveLearningPath, StudySession

        student = get_object_or_404(User, pk=pk, role='student')
        attempts = QuizAttempt.objects.filter(student=student, completed_at__isnull=False)

        completed_units = attempts.values('quiz__lesson__order').distinct().count()
        avg_score = attempts.aggregate(a=Avg('score'))['a']
        # 線上時數統一以 StudySession 心跳時段計（時段列表下方每日圖重用）
        session_rows = list(StudySession.objects.filter(student=student)
                            .values('started_at', 'last_seen'))
        hours = sum(
            max(0.0, (r['last_seen'] - r['started_at']).total_seconds())
            for r in session_rows) / 3600
        mastery = AdaptiveLearningPath.objects.filter(student=student).aggregate(
            a=Avg('current_level'))['a']

        # 重做次數：同一 quiz 作答 >=2 的份數
        quiz_counts = attempts.values('quiz_id').annotate(c=Count('id'))
        retake_count = sum(1 for r in quiz_counts if r['c'] >= 2)

        # 歷史 level 軌跡：每次完成的測驗都是一個點，重做亦保留。
        # level 取該次實際作答課程的難度，而非目前 AdaptiveLearningPath 快照。
        difficulty_to_level = {'beginner': 1, 'intermediate': 2, 'advanced': 3}
        trajectory = [
            {
                'unit': row['quiz__lesson__order'],
                'level': difficulty_to_level.get(row['quiz__lesson__course__difficulty'], 2),
                'score': round(row['score'], 1),
                'completed_at': row['completed_at'],
                'duration_seconds': max(0, round(
                    (row['completed_at'] - row['started_at']).total_seconds()
                )) if row['completed_at'] and row['started_at'] else None,
            }
            for row in attempts.values(
                'quiz__lesson__order',
                'quiz__lesson__course__difficulty',
                'score',
                'started_at',
                'completed_at',
            ).order_by('completed_at', 'id')
        ]

        # 每單元分數：該生 vs 班級平均（個人圖表用）
        stu_unit = {
            r['u']: r['a']
            for r in attempts.values(u=F('quiz__lesson__order')).annotate(a=Avg('score'))
        }
        cls_unit = {
            r['u']: r['a']
            for r in QuizAttempt.objects.filter(
                student__role='student', completed_at__isnull=False)
            .values(u=F('quiz__lesson__order')).annotate(a=Avg('score'))
        }
        unit_scores = [
            {'unit': u,
             'score': round(stu_unit[u], 1) if stu_unit.get(u) is not None else None,
             'class_avg': round(cls_unit[u], 1) if cls_unit.get(u) is not None else None}
            for u in range(1, 9)
        ]

        # 每日使用時間（分鐘）：與 _summarize_sessions 相同的時段長度定義
        from django.utils import timezone as tz
        daily = {}
        for s in session_rows:
            started = s['started_at']
            day = (tz.localtime(started) if tz.is_aware(started) else started).date()
            mins = max(0.0, (s['last_seen'] - s['started_at']).total_seconds() / 60)
            daily[day] = daily.get(day, 0.0) + mins
        daily_usage = [
            {'date': day.isoformat(), 'minutes': round(m, 1)}
            for day, m in sorted(daily.items())
        ]

        # 個人完整錯題紀錄：每一筆錯誤 Answer 都保留，不去重、不推測是否已修正。
        from apps.assessments.models import Choice
        wrong_rows = list(Answer.objects.filter(
            attempt__student=student, is_correct=False,
        ).values(
            'id', 'attempt_id', 'question_id', 'student_answer',
            unit=F('question__quiz__lesson__order'),
            question_order=F('question__order'),
            question_text=F('question__content'),
            qtype=F('question__question_type'),
            answer_key=F('question__correct_answer'),
            completed_at=F('attempt__completed_at'),
        ).order_by('-attempt__completed_at', '-id'))
        selected_choice_ids = set()
        choice_question_ids = set()
        for row in wrong_rows:
            if row['qtype'] in ('multiple_choice', 'true_false'):
                choice_question_ids.add(row['question_id'])
                try:
                    selected_choice_ids.add(int(row['student_answer']))
                except (TypeError, ValueError):
                    pass
        selected_choices = Choice.objects.in_bulk(selected_choice_ids)
        correct_choices = {
            choice.question_id: choice.content
            for choice in Choice.objects.filter(
                question_id__in=choice_question_ids, is_correct=True)
        }
        wrong_answers = []
        for row in wrong_rows:
            submitted = (row['student_answer'] or '').strip() or '（未填）'
            correct = (row['answer_key'] or '').strip() or '—'
            if row['qtype'] in ('multiple_choice', 'true_false'):
                try:
                    selected = selected_choices.get(int(row['student_answer']))
                except (TypeError, ValueError):
                    selected = None
                submitted = selected.content if selected else submitted
                correct = correct_choices.get(row['question_id'], correct)
            wrong_answers.append({
                'id': row['id'], 'attempt_id': row['attempt_id'],
                'unit': row['unit'], 'question_order': row['question_order'],
                'question': row['question_text'], 'qtype': row['qtype'],
                'student_answer': submitted, 'correct_answer': correct,
                'completed_at': row['completed_at'],
            })

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
            'unit_scores': unit_scores,
            'daily_usage': daily_usage,
            'wrong_answers': wrong_answers,
            'compare': {
                'score': round(avg_score, 1) if avg_score is not None else None,
                'class_score': round(class_avg, 1) if class_avg is not None else None,
            },
            'usage': _usage_student_summary(student),
        })


class MyReportView(views.APIView):
    """學生個人成長報表（學生本人可看）。

    刻意不顯示 Level 1/2/3 標籤（學生視角避免標籤化），只呈現：
    學習成效（平均分、完成單元）、使用時間與解題能力。
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
            'usage': _usage_student_summary(student),
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
    if field_type == 'JSONField' and isinstance(value, str):
        return json.loads(value or '{}')
    return value


def _audit_snapshot(obj):
    result = {}
    for field in obj._meta.concrete_fields:
        value = getattr(obj, field.attname)
        if value is None or isinstance(value, (str, int, float, bool, list, dict)):
            result[field.name] = value
        else:
            result[field.name] = str(value)
    return result


class AdminDataView(views.APIView):
    permission_classes = [IsManagementUser]

    CONFIG = {
        'users': {
            'model': ('users', 'User'),
            'title': '使用者',
            'search': ['username', 'email', 'student_id'],
            'order': ['role', 'username'],
            'columns': ['id', 'username', 'first_name', 'email', 'role', 'student_id',
                        'school_short_name', 'school_name', 'preferred_programming_language',
                        'must_change_password', 'is_active', 'date_joined'],
            'editable': ['first_name', 'email', 'role', 'student_id', 'gender',
                         'school_short_name', 'school_name', 'preferred_programming_language',
                         'import_note', 'must_change_password', 'is_active'],
            'create': ['username', 'first_name', 'email', 'password', 'role', 'student_id',
                       'gender', 'school_short_name', 'school_name',
                       'preferred_programming_language', 'import_note',
                       'must_change_password', 'is_active'],
            'filters': {'role': ['student', 'teacher', 'admin'], 'is_active': [True, False]},
        },
        'data_audits': {
            'model': ('users', 'DataChangeAudit'), 'title': '資料異動稽核',
            'search': ['actor__username', 'model_label', 'object_pk', 'reason'], 'order': ['-occurred_at'],
            'columns': ['id', 'actor', 'model_label', 'object_pk', 'action', 'occurred_at', 'reason'],
            'editable': [], 'create': [], 'filters': {'action': ['create', 'update', 'delete']},
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
            'columns': ['id', 'course', 'title', 'order', 'duration_minutes'],
            'editable': ['course', 'title', 'content', 'order', 'duration_minutes'],
            'create': ['course', 'title', 'content', 'order', 'duration_minutes'],
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
            'filters': {'question_type': ['multiple_choice', 'true_false', 'short_answer', 'coding', 'fill_blank']},
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
        'question_interactions': {
            'model': ('assessments', 'QuestionInteraction'),
            'title': '逐題互動紀錄',
            'search': ['attempt__student__username', 'question__content'],
            'order': ['-last_viewed_at'],
            'columns': ['id', 'attempt', 'question', 'first_viewed_at', 'last_viewed_at',
                        'duration_ms', 'answer_revision_count', 'submitted_at'],
            'editable': [], 'create': [], 'filters': {},
        },
        'login_events': {
            'model': ('users', 'LoginEvent'),
            'title': '登入事件',
            'search': ['user__username', 'username_attempt', 'ip_address', 'user_agent'],
            'order': ['-occurred_at'],
            'columns': ['id', 'event_type', 'user', 'username_attempt', 'occurred_at',
                        'ip_address', 'user_agent'],
            'editable': [], 'create': [],
            'filters': {'event_type': ['login_success', 'login_failed', 'logout']},
        },
        'study_sessions': {
            'model': ('learning', 'StudySession'),
            'title': '使用時段',
            'search': ['student__username', 'user_agent'],
            'order': ['-started_at'],
            'columns': ['id', 'student', 'started_at', 'last_seen', 'ended_at',
                        'active_seconds', 'end_reason'],
            'editable': [], 'create': [], 'filters': {},
        },
        'student_events': {
            'model': ('learning', 'StudentEvent'),
            'title': '學生事件流水帳',
            'search': ['student__username', 'event_type', 'page_url'],
            'order': ['-occurred_at', '-id'],
            'columns': ['id', 'event_uuid', 'student', 'event_type', 'course', 'lesson',
                        'quiz', 'question', 'occurred_at', 'received_at', 'duration_ms', 'page_url'],
            'editable': [], 'create': [], 'filters': {},
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
            'columns': ['id', 'student', 'lesson', 'status', 'time_spent_seconds', 'last_accessed', 'completed_at'],
            'editable': ['student', 'lesson', 'status', 'time_spent_seconds', 'completed_at'],
            'create': ['student', 'lesson', 'status', 'time_spent_seconds', 'completed_at'],
            'filters': {'status': ['not_started', 'in_progress', 'completed']},
        },
        'unit_summaries': {
            'model': ('learning', 'StudentUnitSummary'),
            'title': '學生單元彙總',
            'search': ['student__username'],
            'order': ['student__username', 'unit_number'],
            'columns': ['id', 'student', 'unit_number', 'current_level', 'attempt_count',
                        'latest_score', 'best_score', 'time_spent_seconds', 'last_activity_at'],
            'editable': [], 'create': [],
            'filters': {'unit_number': [1, 2, 3, 4, 5, 6, 7, 8], 'current_level': [1, 2, 3]},
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
        from .models import DataChangeAudit
        DataChangeAudit.objects.create(
            actor=request.user, model_label=obj._meta.label, object_pk=str(obj.pk),
            action='create', after=_audit_snapshot(obj),
        )
        return response.Response(self.serialize(obj, config), status=status.HTTP_201_CREATED)

    def patch(self, request, key, pk):
        config, model = self.get_config(key)
        if not config:
            return response.Response({'detail': 'Unknown data model.'}, status=status.HTTP_404_NOT_FOUND)
        obj = get_object_or_404(model, pk=pk)
        before = _audit_snapshot(obj)
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
        from .models import DataChangeAudit
        DataChangeAudit.objects.create(
            actor=request.user, model_label=obj._meta.label, object_pk=str(obj.pk),
            action='update', before=before, after=_audit_snapshot(obj),
            reason=str(request.data.get('_change_reason') or '')[:500],
        )
        return response.Response(self.serialize(obj, config))

    # 學生作答／學習歷程屬研究資料，受保護不開放從資料管理直接刪除
    PROTECTED_STUDENT_DATA = {
        'attempts', 'progress', 'recommendations', 'adaptive', 'unit_summaries',
        'question_interactions', 'login_events', 'study_sessions', 'student_events',
        'data_audits',
    }

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
