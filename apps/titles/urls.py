"""
URLs for titles app.
"""
from django.urls import path
from . import views

app_name = 'titles'

urlpatterns = [
    path('<str:omdb_id>/', views.TitleDetailView.as_view(), name='detail'),
    path('api/search/', views.SearchAjaxView.as_view(), name='search_ajax'),
    path('<str:omdb_id>/rate/', views.add_rating, name='rate'),
    path('<str:omdb_id>/watchlist/', views.add_watchlist, name='add_watchlist'),
    path('<str:omdb_id>/watchlist/remove/', views.remove_watchlist, name='remove_watchlist'),
]
