"""
URL configuration for RateMyShow project.
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),
    path('titles/', include('apps.titles.urls')),
    path('accounts/', include('apps.users.urls')),
    path('ratings/', include('apps.ratings.urls')),
    path('recommendations/', include('apps.recommendations.urls')),
    path('api/', include('apps.titles.api_urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Error handlers
handler404 = 'apps.core.views.page_not_found'
handler500 = 'apps.core.views.server_error'
handler403 = 'apps.core.views.permission_denied'
