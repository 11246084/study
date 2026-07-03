"""研究事件的共通情境：用戶端時間、session 繫結、tab 識別。

所有 StudentEvent 建立點都應套用，讓每筆事件可回答：
「操作真正發生在何時」「屬於哪一段使用時段」「來自哪個分頁」。
"""
from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from django.utils.dateparse import parse_datetime

# 用戶端時間與伺服器時間差超過此範圍視為時鐘異常，改用伺服器時間
MAX_CLOCK_SKEW = timedelta(days=7)


def parse_client_time(raw):
    """解析前端送來的 ISO 時間；不合理（缺漏、時鐘亂掉）回傳 None。

    專案 USE_TZ=False（MySQL 以本地時間儲存），故統一轉成本地 naive 時間。
    """
    if not raw:
        return None
    occurred = parse_datetime(str(raw))
    if occurred is None:
        return None
    if settings.USE_TZ:
        if timezone.is_naive(occurred):
            occurred = timezone.make_aware(occurred, timezone.utc)
    else:
        if timezone.is_aware(occurred):
            occurred = timezone.make_naive(occurred, timezone.get_default_timezone())
    if abs(timezone.now() - occurred) > MAX_CLOCK_SKEW:
        return None
    return occurred


def current_session(student):
    """該生目前的活躍使用時段（最後活動在 GAP 內且未結束）。"""
    from .models import StudySession
    gap = timedelta(minutes=StudySession.GAP_MINUTES)
    return (
        StudySession.objects
        .filter(student=student, ended_at__isnull=True,
                last_seen__gte=timezone.now() - gap)
        .order_by('-last_seen')
        .first()
    )


def event_context(request, payload=None):
    """回傳 (create_kwargs, metadata_extra)。

    create_kwargs: occurred_at（用戶端時間，缺省時模型預設伺服器時間）、session
    metadata_extra: tab_uuid（無 schema 變更，收在 metadata）
    """
    payload = payload if payload is not None else request.data
    getter = payload.get if hasattr(payload, 'get') else (lambda key: None)

    kwargs = {}
    occurred = parse_client_time(getter('client_occurred_at'))
    if occurred:
        kwargs['occurred_at'] = occurred

    session = current_session(request.user)
    if session:
        kwargs['session'] = session

    metadata_extra = {}
    tab_uuid = getter('tab_uuid')
    if tab_uuid:
        metadata_extra['tab_uuid'] = str(tab_uuid)[:64]
    return kwargs, metadata_extra
