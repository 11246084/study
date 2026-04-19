from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from rest_framework_simplejwt.views import TokenRefreshView

FRONTEND_DIR = settings.BASE_DIR.parent / 'frontend'


def serve_no_cache(request, path=None, document_root=None):
    """包裝 Django 靜態服務，加上 no-cache 回應標頭，防止瀏覽器快取 HTML。"""
    response = serve(request, path or 'index.html', document_root=document_root)
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.users.urls')),
    path('api/courses/', include('apps.courses.urls')),
    path('api/assessments/', include('apps.assessments.urls')),
    path('api/learning/', include('apps.learning.urls')),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', serve_no_cache, {'document_root': FRONTEND_DIR}),
    re_path(r'^(?P<path>.+)$', serve_no_cache, {'document_root': FRONTEND_DIR}),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
