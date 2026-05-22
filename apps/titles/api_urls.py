"""
API URLs for titles app.
"""
from django.urls import path
from rest_framework.routers import DefaultRouter
from . import api_views

app_name = 'titles_api'

router = DefaultRouter()

urlpatterns = [
    path('titles/search/', api_views.TitleSearchAPI.as_view(), name='search'),
    path('titles/<str:omdb_id>/', api_views.TitleDetailAPI.as_view(), name='detail'),
] + router.urls
