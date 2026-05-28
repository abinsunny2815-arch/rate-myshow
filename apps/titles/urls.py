"""
URLs for titles app.
"""
from django.urls import path
from . import views

app_name = 'titles'

urlpatterns = [
    path('<str:omdb_id>/', views.TitleDetailView.as_view(), name='detail'),
    path('api/search/', views.SearchAjaxView.as_view(), name='search_ajax'),
    path('api/watchlist-status/<str:omdb_id>/', views.get_watchlist_status, name='watchlist_status'),
    
    # Watchlist actions
    path('<str:omdb_id>/rate/', views.add_rating, name='rate'),
    path('<str:omdb_id>/watchlist/add/', views.add_watchlist, name='add_watchlist'),
    path('<str:omdb_id>/watchlist/remove/', views.remove_watchlist, name='remove_watchlist'),
    path('<str:omdb_id>/mark-watched/', views.mark_as_watched, name='mark_watched'),
    
    # User watchlist/watched pages
    path('my-watchlist/', views.UserWatchlistView.as_view(), name='my_watchlist'),
    path('my-watched/', views.UserWatchedView.as_view(), name='my_watched'),
]
