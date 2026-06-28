import csv
import io
import math

from django.db import transaction
from rest_framework import generics, response, status, views

from apps.users.models import User
from apps.users.views import IsManagementUser
from .models import SurveyScale, SurveyScore
from .serializers import SurveyScaleSerializer


def validate_score(scale, phase, raw):
    """Convert and validate one research score against its scale definition."""
    if scale.post_only and phase == 'pre':
        raise ValueError('此量表僅允許後測資料。')
    value = float(raw)
    if not math.isfinite(value):
        raise ValueError('分數必須是有限數值。')
    if not scale.score_min <= value <= scale.score_max:
        raise ValueError(f'分數必須介於 {scale.score_min:g} 與 {scale.score_max:g}。')
    return value


class ScaleListView(generics.ListAPIView):
    """列出啟用中的問卷構念（供登錄介面與報表標籤使用）。"""
    serializer_class = SurveyScaleSerializer
    permission_classes = [IsManagementUser]
    pagination_class = None

    def get_queryset(self):
        return SurveyScale.objects.filter(is_active=True)


class ScoreGridView(views.APIView):
    """批次登錄用：給定構念+階段，回傳全班學生與其目前分數。

    GET /api/surveys/scores/?scale=<key>&phase=<pre|post>
    """
    permission_classes = [IsManagementUser]

    def get(self, request):
        scale_key = request.GET.get('scale')
        phase = request.GET.get('phase', 'pre')
        if phase not in ('pre', 'post'):
            return response.Response({'detail': 'phase 須為 pre 或 post'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            scale = SurveyScale.objects.get(key=scale_key)
        except SurveyScale.DoesNotExist:
            return response.Response({'detail': '找不到此構念'}, status=status.HTTP_404_NOT_FOUND)

        existing = {
            s.student_id: s.score
            for s in SurveyScore.objects.filter(scale=scale, phase=phase)
        }
        students = User.objects.filter(role='student').order_by('username')
        rows = [{
            'student_id': u.id,
            'username': u.username,
            'student_no': u.student_id,
            'score': existing.get(u.id),
        } for u in students]
        return response.Response({
            'scale': SurveyScaleSerializer(scale).data,
            'phase': phase,
            'rows': rows,
        })


class ScoreBatchView(views.APIView):
    """批次寫入/更新某構念+階段的分數。

    POST /api/surveys/scores/batch/
    body: { "scale": "<key>", "phase": "pre", "scores": { "<student_id>": 3.5, ... } }
    空字串/ null 代表刪除該筆。
    """
    permission_classes = [IsManagementUser]

    def post(self, request):
        scale_key = request.data.get('scale')
        phase = request.data.get('phase')
        scores = request.data.get('scores') or {}
        if phase not in ('pre', 'post'):
            return response.Response({'detail': 'phase 須為 pre 或 post'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            scale = SurveyScale.objects.get(key=scale_key)
        except SurveyScale.DoesNotExist:
            return response.Response({'detail': '找不到此構念'}, status=status.HTTP_404_NOT_FOUND)

        saved, removed, errors = 0, 0, []
        valid_ids = set(User.objects.filter(role='student').values_list('id', flat=True))
        with transaction.atomic():
            for sid, raw in scores.items():
                try:
                    sid = int(sid)
                except (TypeError, ValueError):
                    errors.append({'student_id': sid, 'value': raw, 'detail': '無效的學生 ID。'})
                    continue
                if sid not in valid_ids:
                    errors.append({'student_id': sid, 'value': raw, 'detail': '找不到學生。'})
                    continue
                if raw in ('', None):
                    deleted, _ = SurveyScore.objects.filter(scale=scale, phase=phase, student_id=sid).delete()
                    removed += 1 if deleted else 0
                    continue
                try:
                    value = validate_score(scale, phase, raw)
                except (TypeError, ValueError) as exc:
                    errors.append({'student_id': sid, 'value': raw, 'detail': str(exc)})
                    continue
                SurveyScore.objects.update_or_create(
                    student_id=sid, scale=scale, phase=phase,
                    defaults={'score': value},
                )
                saved += 1
        return response.Response({'saved': saved, 'removed': removed, 'errors': errors})


class ScoreImportView(views.APIView):
    """CSV 匯入（寬表格式，方便從 Excel 貼上）。

    POST /api/surveys/scores/import/
    body: { "csv": "<csv 內容>" }  或 multipart file 欄位 "file"
    第一欄為學生識別（username 或學號），其餘欄位標題格式為 <scale_key>_<pre|post>，
    例如 motivation_intrinsic_pre, anxiety_post。空白儲存格略過。
    """
    permission_classes = [IsManagementUser]

    def post(self, request):
        raw = request.data.get('csv')
        if not raw and 'file' in request.FILES:
            raw = request.FILES['file'].read().decode('utf-8-sig', errors='ignore')
        if not raw:
            return response.Response({'detail': '請提供 csv 內容或 file'}, status=status.HTTP_400_BAD_REQUEST)
        if len(raw.encode('utf-8')) > 2 * 1024 * 1024:
            return response.Response({'detail': 'CSV 不得超過 2 MB。'}, status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)

        reader = csv.reader(io.StringIO(raw))
        rows = [r for r in reader if any(c.strip() for c in r)]
        if len(rows) < 2:
            return response.Response({'detail': 'CSV 至少需有標題列與一列資料'}, status=status.HTTP_400_BAD_REQUEST)

        header = [c.strip() for c in rows[0]]
        # 解析欄位 → (scale, phase)
        col_map = {}
        scales_by_key = {s.key: s for s in SurveyScale.objects.all()}
        unknown_cols = []
        for idx, col in enumerate(header[1:], start=1):
            if '_' not in col:
                continue
            key, _, phase = col.rpartition('_')
            if phase in ('pre', 'post') and key in scales_by_key:
                col_map[idx] = (scales_by_key[key], phase)
            else:
                unknown_cols.append(col)

        users = list(User.objects.filter(role='student'))
        by_username = {u.username: u for u in users}
        by_no = {u.student_id: u for u in users if u.student_id}

        saved, skipped_rows, unmatched, errors = 0, 0, [], []
        for row_number, row in enumerate(rows[1:], start=2):
            ident = (row[0] if row else '').strip()
            student = by_username.get(ident) or by_no.get(ident)
            if not student:
                if ident:
                    unmatched.append(ident)
                skipped_rows += 1
                continue
            for idx, (scale, phase) in col_map.items():
                if idx >= len(row):
                    continue
                cell = (row[idx] or '').strip()
                if cell == '':
                    continue
                try:
                    value = validate_score(scale, phase, cell)
                except (TypeError, ValueError) as exc:
                    errors.append({
                        'row': row_number,
                        'column': header[idx],
                        'value': cell,
                        'detail': str(exc),
                    })
                    continue
                SurveyScore.objects.update_or_create(
                    student=student, scale=scale, phase=phase,
                    defaults={'score': value},
                )
                saved += 1
        return response.Response({
            'saved': saved,
            'unmatched_students': unmatched,
            'unknown_columns': unknown_cols,
            'matched_columns': [f'{s.key}_{p}' for s, p in col_map.values()],
            'errors': errors,
        })
