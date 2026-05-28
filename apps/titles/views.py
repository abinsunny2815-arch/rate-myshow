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


class UserWatchlistView(LoginRequiredMixin, ListView):
    """Display user's to-watch watchlist."""
    template_name = 'titles/watchlist.html'
    context_object_name = 'watchlist_items'
    paginate_by = 24
    
    def get_queryset(self):
        return Watchlist.objects.filter(
            user=self.request.user,
            status='to-watch'
        ).select_related('title').order_by('-priority', '-added_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'My Watchlist'
        context['total_count'] = self.get_queryset().count()
        return context


class UserWatchedView(LoginRequiredMixin, ListView):
    """Display user's watched movies."""
    template_name = 'titles/watched.html'
    context_object_name = 'watched_items'
    paginate_by = 24
    
    def get_queryset(self):
        return Watchlist.objects.filter(
            user=self.request.user,
            status='watched'
        ).select_related('title').order_by('-watched_at', '-added_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'My Watched Movies'
        context['total_count'] = self.get_queryset().count()
        
        # Get ratings for watched items
        watched_ids = [item.title_id for item in self.get_queryset()]
        ratings = Rating.objects.filter(
            user=self.request.user,
            title_id__in=watched_ids
        ).values('title_id', 'score')
        rating_dict = {r['title_id']: r['score'] for r in ratings}
        context['rating_dict'] = rating_dict
        
        return context


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
    
    if status not in dict(Watchlist.STATUS_CHOICES):
        return JsonResponse({'error': 'Invalid status'}, status=400)
    
    watchlist, created = Watchlist.objects.update_or_create(
        user=request.user,
        title=title,
        defaults={'status': status}
    )
    
    request.user.update_stats()
    
    return JsonResponse({
        'success': True,
        'created': created,
        'status': status,
        'is_watched': watchlist.is_watched
    })


@login_required
@require_POST
def mark_as_watched(request, omdb_id):
    """Mark a title as watched."""
    title = get_object_or_404(Title, omdb_id=omdb_id)
    
    # Get or create watchlist entry
    watchlist, created = Watchlist.objects.get_or_create(
        user=request.user,
        title=title
    )
    
    watchlist.mark_as_watched()
    request.user.update_stats()
    
    return JsonResponse({
        'success': True,
        'is_watched': True,
        'watched_at': watchlist.watched_at.isoformat() if watchlist.watched_at else None
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


@login_required
def get_watchlist_status(request, omdb_id):
    """Get watchlist status for a title (for AJAX)."""
    title = get_object_or_404(Title, omdb_id=omdb_id)
    
    watchlist = Watchlist.objects.filter(
        user=request.user,
        title=title
    ).first()
    
    rating = Rating.objects.filter(
        user=request.user,
        title=title
    ).first()
    
    return JsonResponse({
        'in_watchlist': watchlist is not None,
        'status': watchlist.status if watchlist else None,
        'is_watched': watchlist.is_watched if watchlist else False,
        'rating': rating.score if rating else None,
        'watched_at': watchlist.watched_at.isoformat() if watchlist and watchlist.watched_at else None
    })
