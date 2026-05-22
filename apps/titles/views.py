"""
Views for titles app.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count
from django.core.paginator import Paginator

from apps.titles.models import Title, Watchlist
from apps.ratings.models import Rating, Review
from apps.core.services import OMDBService
from apps.recommendations.services import RecommendationEngine


class TitleDetailView(DetailView):
    """Detailed view for a movie/TV show."""
    model = Title
    template_name = 'titles/detail.html'
    context_object_name = 'title'
    slug_field = 'omdb_id'
    slug_url_kwarg = 'omdb_id'
    
    def get_object(self, queryset=None):
        omdb_id = self.kwargs.get('omdb_id')
        
        # Try to get from DB, if not found sync from OMDB
        try:
            return Title.objects.get(omdb_id=omdb_id)
        except Title.DoesNotExist:
            service = OMDBService()
            title = service.sync_title_to_db(omdb_id)
            if not title:
                raise Http404("Title not found")
            return title
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        title = self.object
        
        # User's rating if exists
        if self.request.user.is_authenticated:
            context['user_rating'] = Rating.objects.filter(
                user=self.request.user,
                title=title
            ).first()
            context['user_review'] = Review.objects.filter(
                user=self.request.user,
                title=title
            ).first()
            context['in_watchlist'] = Watchlist.objects.filter(
                user=self.request.user,
                title=title
            ).first()
        
        # All reviews
        context['reviews'] = Review.objects.filter(
            title=title
        ).select_related('user').order_by('-helpful_count', '-created_at')[:20]
        
        # Rating distribution
        ratings = Rating.objects.filter(title=title).aggregate(
            avg=Avg('score'),
            count=Count('id')
        )
        context['avg_rating'] = ratings['avg'] or 0
        context['total_ratings'] = ratings['count']
        
        # Similar titles (content-based)
        similar = title.genres.all().values_list('titles', flat=True).distinct()[:10]
        context['similar_titles'] = Title.objects.filter(id__in=similar).exclude(id=title.id)
        
        return context


class SearchAjaxView(DetailView):
    """AJAX search for titles."""
    
    def get(self, request):
        query = request.GET.get('q', '').strip()
        if len(query) < 2:
            return JsonResponse({'results': []})
        
        results = Title.objects.filter(
            title__icontains=query
        ).values('omdb_id', 'title', 'year', 'poster_url', 'type')[:20]
        
        return JsonResponse({'results': list(results)})


@login_required
@require_POST
def add_rating(request, omdb_id):
    """Add or update a rating."""
    title = get_object_or_404(Title, omdb_id=omdb_id)
    score = request.POST.get('score')
    
    try:
        score = float(score)
        if not (1 <= score <= 10):
            return JsonResponse({'error': 'Rating must be between 1 and 10'}, status=400)
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Invalid rating'}, status=400)
    
    rating, created = Rating.objects.update_or_create(
        user=request.user,
        title=title,
        defaults={'score': score}
    )
    
    # Update title stats
    title.update_ratings()
    
    # Trigger recommendation update
    engine = RecommendationEngine()
    engine.update_recommendations_for_user(request.user)
    
    return JsonResponse({
        'success': True,
        'created': created,
        'rating': score,
        'avg_rating': title.avg_rating,
        'rating_count': title.rating_count
    })


@login_required
@require_POST
def add_watchlist(request, omdb_id):
    """Add title to watchlist."""
    title = get_object_or_404(Title, omdb_id=omdb_id)
    status = request.POST.get('status', 'to-watch')
    
    watchlist, created = Watchlist.objects.update_or_create(
        user=request.user,
        title=title,
        defaults={'status': status}
    )
    
    request.user.update_stats()
    
    return JsonResponse({
        'success': True,
        'created': created,
        'status': status
    })


@login_required
@require_POST
def remove_watchlist(request, omdb_id):
    """Remove title from watchlist."""
    title = get_object_or_404(Title, omdb_id=omdb_id)
    
    Watchlist.objects.filter(
        user=request.user,
        title=title
    ).delete()
    
    request.user.update_stats()
    
    return JsonResponse({'success': True})
