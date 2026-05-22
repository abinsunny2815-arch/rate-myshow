"""
Views for users app (authentication and profiles).
"""
from django.shortcuts import render, redirect
from django.views.generic import CreateView, UpdateView, DetailView, ListView
from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetConfirmView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Count

from apps.users.models import CustomUser, UserActivity
from apps.titles.models import Watchlist
from apps.ratings.models import Rating, Review
from . import forms


class RegisterView(CreateView):
    """User registration."""
    model = CustomUser
    form_class = forms.CustomUserCreationForm
    template_name = 'auth/register.html'
    success_url = reverse_lazy('core:home')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.save()
        login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
        messages.success(self.request, 'Welcome to RateMyShow!')
        return response


class CustomLoginView(LoginView):
    """Custom login view."""
    template_name = 'auth/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('core:home')


class ProfileView(LoginRequiredMixin, DetailView):
    """User profile page."""
    model = CustomUser
    template_name = 'users/profile.html'
    context_object_name = 'user_obj'
    
    def get_object(self):
        return self.request.user
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.object
        
        context['ratings_count'] = Rating.objects.filter(user=user).count()
        context['reviews_count'] = Review.objects.filter(user=user).count()
        context['watchlist_count'] = Watchlist.objects.filter(user=user).count()
        
        context['recent_ratings'] = Rating.objects.filter(user=user).select_related(
            'title'
        ).order_by('-created_at')[:10]
        
        context['recent_reviews'] = Review.objects.filter(user=user).select_related(
            'title'
        ).order_by('-created_at')[:10]
        
        context['watchlist'] = Watchlist.objects.filter(
            user=user,
            status='to-watch'
        ).select_related('title')[:20]
        
        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    """Edit user profile."""
    model = CustomUser
    form_class = forms.CustomUserChangeForm
    template_name = 'users/profile_edit.html'
    success_url = reverse_lazy('users:profile')
    
    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Profile updated successfully!')
        return response


class WatchlistView(LoginRequiredMixin, ListView):
    """View user's watchlist."""
    model = Watchlist
    template_name = 'users/watchlist.html'
    context_object_name = 'watchlist_items'
    paginate_by = 20
    
    def get_queryset(self):
        return Watchlist.objects.filter(user=self.request.user).select_related('title')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        status_filter = self.request.GET.get('status', 'to-watch')
        
        context['statuses'] = Watchlist.STATUS_CHOICES
        context['current_status'] = status_filter
        
        if status_filter:
            context['watchlist_items'] = Watchlist.objects.filter(
                user=self.request.user,
                status=status_filter
            ).select_related('title')
        
        return context


class RatingsView(LoginRequiredMixin, ListView):
    """View user's ratings."""
    model = Rating
    template_name = 'users/ratings.html'
    context_object_name = 'ratings'
    paginate_by = 30
    
    def get_queryset(self):
        sort = self.request.GET.get('sort', '-created_at')
        return Rating.objects.filter(user=self.request.user).select_related('title').order_by(sort)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ratings = Rating.objects.filter(user=self.request.user)
        
        # Stats
        context['total_ratings'] = ratings.count()
        if ratings.exists():
            context['avg_rating'] = ratings.aggregate(models.Avg('score'))['score__avg']
        
        return context


from django.db import models
