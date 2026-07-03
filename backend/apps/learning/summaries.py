"""StudentUnitSummary 的更新邏輯。

彙總表是「給人看」的資料層：原始事件與作答仍是唯一的真相來源，
這裡的函式只負責把它們折疊成一列一意義的摘要，可隨時整表重算。
"""
from django.utils import timezone

from .models import AdaptiveLearningPath, LearningProgress, StudentUnitSummary


def _summary(student, unit_number):
    summary, _ = StudentUnitSummary.objects.get_or_create(
        student=student, unit_number=unit_number,
    )
    return summary


def record_attempt(student, unit_number, score, level, when=None):
    """交卷後更新該單元摘要（作答次數、最近/最佳分數、目前等級）。"""
    when = when or timezone.now()
    summary = _summary(student, unit_number)
    summary.attempt_count += 1
    summary.latest_score = score
    summary.best_score = score if summary.best_score is None else max(summary.best_score, score)
    summary.current_level = level
    summary.last_activity_at = when
    summary.save()


def record_lesson_time(student, unit_number, seconds, when=None):
    """教材心跳累計停留秒數。"""
    when = when or timezone.now()
    summary = _summary(student, unit_number)
    summary.time_spent_seconds += seconds
    summary.last_activity_at = when
    summary.save()


def sync_level(student, unit_number, level):
    """適性路徑等級變動時同步到摘要。"""
    summary = _summary(student, unit_number)
    if summary.current_level != level:
        summary.current_level = level
        summary.save(update_fields=['current_level', 'updated_at'])


def rebuild_for_student(student):
    """由原始資料（作答、閱讀進度、適性路徑）重算該學生的 8 列摘要。"""
    from django.db.models import Count, F, Max, Sum
    from apps.assessments.models import QuizAttempt

    levels = {
        p.unit_number: p.current_level
        for p in AdaptiveLearningPath.objects.filter(student=student)
    }
    attempts = (
        QuizAttempt.objects.filter(student=student, completed_at__isnull=False)
        .values(unit=F('quiz__lesson__order'))
        .annotate(n=Count('id'), best=Max('score'), last_at=Max('completed_at'))
    )
    attempt_rows = {row['unit']: row for row in attempts}
    time_rows = {
        row['unit']: row['t'] or 0
        for row in LearningProgress.objects.filter(student=student)
        .values(unit=F('lesson__order'))
        .annotate(t=Sum('time_spent_seconds'))
    }

    for unit in range(1, 9):
        row = attempt_rows.get(unit)
        latest_score = None
        if row:
            latest = (
                QuizAttempt.objects.filter(
                    student=student, completed_at__isnull=False, quiz__lesson__order=unit,
                ).order_by('-completed_at').first()
            )
            latest_score = latest.score if latest else None
        if not row and unit not in time_rows and unit not in levels:
            continue
        summary = _summary(student, unit)
        summary.attempt_count = row['n'] if row else 0
        summary.best_score = row['best'] if row else None
        summary.latest_score = latest_score
        summary.time_spent_seconds = time_rows.get(unit, 0)
        summary.current_level = levels.get(unit, 2)
        summary.last_activity_at = row['last_at'] if row else summary.last_activity_at
        summary.save()
