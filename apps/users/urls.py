"""
URLs for users app.
"""
from django.urls import path
from django.contrib.auth.views import LogoutView, PasswordResetView, PasswordResetConfirmView
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='core:home'), name='logout'),
    path('password-reset/', PasswordResetView.as_view(template_name='auth/password_reset.html'), name='password_reset'),
    path('password-reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(template_name='auth/password_reset_confirm.html'), name='password_reset_confirm'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views.ProfileEditView.as_view(), name='profile_edit'),
    path('watchlist/', views.WatchlistView.as_view(), name='watchlist'),
    path('ratings/', views.RatingsView.as_view(), name='ratings'),
]
