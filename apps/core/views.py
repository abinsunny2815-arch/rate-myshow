"""
Views for core app.
"""
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta

from apps.titles.models import Title, Genre
from apps.ratings.models import Rating, Review
from apps.recommendations.models import Recommendation


class HomeView(TemplateView):
    """Home page with trending and personalized content."""
    template_name = 'core/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Trending this week
        week_ago = timezone.now() - timedelta(days=7)
        trending = Title.objects.filter(
            ratings__created_at__gte=week_ago
        ).annotate(
            rating_count=Count('ratings')
        ).order_by('-rating_count')[:10]
        
        context['trending'] = trending
        
        # Popular movies
        context['popular_movies'] = Title.objects.filter(
            type='movie',
            rating_count__gt=10
        ).order_by('-avg_rating', '-rating_count')[:10]
        
        # Top TV shows
        context['top_tv_shows'] = Title.objects.filter(
            type='series',
            rating_count__gt=5
        ).order_by('-avg_rating', '-rating_count')[:10]
        
        # Recommendations for logged-in users
        if self.request.user.is_authenticated:
            context['recommendations'] = Recommendation.objects.filter(
                user=self.request.user,
                is_dismissed=False
            ).select_related('title')[:10]
        
        # Recent activity
        context['recent_reviews'] = Review.objects.select_related(
            'user', 'title'
        ).order_by('-created_at')[:5]
        
        return context


class SearchView(TemplateView):
    """Global search for titles."""
    template_name = 'core/search.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '').strip()
        
        if query:
            context['results'] = Title.objects.filter(
                Q(title__icontains=query) | Q(plot__icontains=query)
            ).order_by('-avg_rating', '-rating_count')[:50]
            context['query'] = query
        
        return context


class TopMoviesView(ListView):
    """Top 250 movies ranked by rating and votes."""
    model = Title
    template_name = 'core/top_movies.html'
    context_object_name = 'movies'
    paginate_by = 50
    
    def get_queryset(self):
        return Title.objects.filter(
            type='movie',
            rating_count__gt=0
        ).order_by('-avg_rating', '-rating_count')


class TopTVShowsView(ListView):
    """Top 250 TV shows ranked by rating and votes."""
    model = Title
    template_name = 'core/top_tv_shows.html'
    context_object_name = 'shows'
    paginate_by = 50
    
    def get_queryset(self):
        return Title.objects.filter(
            type='series',
            rating_count__gt=0
        ).order_by('-avg_rating', '-rating_count')


class GenreListView(ListView):
    """Browse by genre."""
    model = Genre
    template_name = 'core/genres.html'
    context_object_name = 'genres'
    paginate_by = 20


class GenreDetailView(DetailView):
    """View all titles in a genre."""
    model = Genre
    template_name = 'core/genre_detail.html'
    context_object_name = 'genre'
    slug_field = 'slug'
    paginate_by = 20
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titles'] = self.object.titles.order_by('-avg_rating', '-rating_count')
        return context


class ActivityFeedView(ListView):
    """Recent user activity feed."""
    template_name = 'core/activity_feed.html'
    context_object_name = 'activities'
    paginate_by = 30
    
    def get_queryset(self):
        return Review.objects.select_related('user', 'title').order_by('-created_at')


class UserProfileView(DetailView):
    """View user profile and their ratings/reviews."""
    template_name = 'core/user_profile.html'
    model = __import__('apps.users.models', fromlist=['CustomUser']).CustomUser
    slug_field = 'username'
    slug_url_kwarg = 'username'
    context_object_name = 'profile_user'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        
        context['ratings'] = Rating.objects.filter(user=user).select_related('title')[:20]
        context['reviews'] = Review.objects.filter(user=user).select_related('title')[:10]
        context['watchlist'] = user.watchlists.filter(status='to-watch')[:20]
        
        return context


# Error handlers
def page_not_found(request, exception):
    """404 error page."""
    return render(request, 'errors/404.html', status=404)


def server_error(request):
    """500 error page."""
    return render(request, 'errors/500.html', status=500)


def permission_denied(request, exception):
    """403 error page."""
    return render(request, 'errors/403.html', status=403)
