"""
URLs for core app.
"""
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('search/', views.SearchView.as_view(), name='search'),
    path('top-movies/', views.TopMoviesView.as_view(), name='top_movies'),
    path('top-tv-shows/', views.TopTVShowsView.as_view(), name='top_tv_shows'),
    path('genres/', views.GenreListView.as_view(), name='genre_list'),
    path('genres/<slug:slug>/', views.GenreDetailView.as_view(), name='genre_detail'),
    path('activity/', views.ActivityFeedView.as_view(), name='activity_feed'),
    path('profile/<slug:username>/', views.UserProfileView.as_view(), name='user_profile'),
]
