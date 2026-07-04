"""
PreviewAsJWTAuthentication
==========================
擴充 JWT 驗證：當 admin 帶 `?preview_as=<id|username>` 或 `X-Preview-As: <id|username>`
header 時，把 request.user 透明替換成那位學生。

用途：admin 在 /admin-shell.html 的「學習路徑」tab 內以 iframe 預覽某學生的視角，
所有 API 自動回傳該學生的資料，無需逐一改 view。

安全：只有 role=admin（或 is_superuser/is_staff）才生效，其他角色帶這個參數一律忽略。
"""

from django.contrib.auth.backends import ModelBackend
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import User


class ExactUsernameBackend(ModelBackend):
    """帳號必須逐字相符才能登入。

    MySQL 的 utf8mb4_unicode_ci 定序把大小寫、全形/半形視為相同，
    導致「TeXt1」「ｔｅｘｔ1」都撈得到 text1 這筆帳號並通過密碼驗證。
    這裡在 Python 層補一道逐字比對，杜絕定序造成的寬鬆登入。
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        user = super().authenticate(request, username=username, password=password, **kwargs)
        if user is None:
            return None
        attempted = username if username is not None else kwargs.get(User.USERNAME_FIELD)
        if attempted is not None and user.get_username() != attempted:
            return None
        return user


class PreviewAsJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        result = super().authenticate(request)
        if result is None:
            return None

        user, validated_token = result

        # 必須是 admin 才允許預覽
        is_admin = (
            getattr(user, 'role', None) == 'admin'
            or getattr(user, 'is_superuser', False)
            or getattr(user, 'is_staff', False)
        )
        if not is_admin:
            return user, validated_token

        # 從 query string 或 header 讀 preview_as
        preview_as = (
            request.GET.get('preview_as')
            or request.META.get('HTTP_X_PREVIEW_AS')
        )
        if not preview_as:
            return user, validated_token

        # 支援數字 ID 或 username 兩種
        try:
            if str(preview_as).isdigit():
                target = User.objects.get(id=int(preview_as), role='student')
            else:
                target = User.objects.get(username=preview_as, role='student')
            request.preview_as_admin = True
            return target, validated_token
        except User.DoesNotExist:
            # 找不到就退回 admin 自己
            return user, validated_token
