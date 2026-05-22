"""
Recommendation engine with content-based and collaborative filtering.
"""
import numpy as np
import logging
from django.db import models
from django.core.cache import cache
from sklearn.metrics.pairwise import cosine_similarity
from apps.titles.models import Title, Genre
from apps.ratings.models import Rating
from apps.users.models import CustomUser
from apps.recommendations.models import Recommendation, UserSimilarity, CollaborativeRating
from typing import List, Tuple, Dict

logger = logging.getLogger(__name__)


class RecommendationEngine:
    """Hybrid recommendation engine combining content and collaborative filtering."""
    
    def __init__(self, min_common_ratings: int = None, similarity_threshold: float = None):
        self.min_common_ratings = min_common_ratings or settings.MIN_COMMON_RATINGS
        self.similarity_threshold = similarity_threshold or settings.SIMILARITY_THRESHOLD
    
    # Content-Based Recommendations
    def get_content_based_recommendations(self, user: CustomUser, limit: int = 10) -> List[Title]:
        """
        Recommend titles based on genres and actors user has rated highly.
        """
        cache_key = f'content_recommendations:{user.id}'
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        # Get user's highly-rated movies (8+)
        high_ratings = Rating.objects.filter(user=user, score__gte=8).select_related('title')
        if not high_ratings.exists():
            return []
        
        # Extract favorite genres and actors
        favorite_genres = set()
        favorite_actors = set()
        for rating in high_ratings:
            favorite_genres.update(rating.title.genres.values_list('id', flat=True))
            favorite_actors.update(rating.title.actors.values_list('id', flat=True))
        
        # Find similar titles (not yet rated)
        already_rated = Rating.objects.filter(user=user).values_list('title_id', flat=True)
        
        recommendations = Title.objects.filter(
            models.Q(genres__id__in=favorite_genres) | models.Q(actors__id__in=favorite_actors)
        ).exclude(
            id__in=already_rated
        ).distinct().order_by('-avg_rating', '-rating_count')[:limit]
        
        recommendations_list = list(recommendations)
        cache.set(cache_key, recommendations_list, 86400)  # Cache for 24 hours
        return recommendations_list
    
    # Collaborative Filtering
    def find_similar_users(self, user: CustomUser, limit: int = 10) -> List[Tuple[CustomUser, float]]:
        """
        Find users with similar rating patterns using cosine similarity.
        """
        cache_key = f'similar_users:{user.id}'
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        # Get all titles rated by the user
        user_ratings = Rating.objects.filter(user=user).select_related('title')
        if not user_ratings.exists():
            return []
        
        user_titles = set(user_ratings.values_list('title_id', flat=True))
        
        # Find other users who rated at least min_common_ratings of the same titles
        other_users = CustomUser.objects.exclude(id=user.id).annotate(
            common_count=models.Count(
                'ratings',
                filter=models.Q(ratings__title_id__in=user_titles)
            )
        ).filter(common_count__gte=self.min_common_ratings)
        
        similar_users = []
        user_rating_dict = {r.title_id: r.score for r in user_ratings}
        
        for other_user in other_users[:50]:  # Check up to 50 users
            # Calculate cosine similarity
            other_ratings = Rating.objects.filter(
                user=other_user,
                title_id__in=user_titles
            ).values_list('title_id', 'score')
            
            if len(other_ratings) < self.min_common_ratings:
                continue
            
            # Create vectors for common titles
            common_titles = [r[0] for r in other_ratings]
            user_vector = np.array([user_rating_dict.get(t_id, 0) for t_id in common_titles])
            other_vector = np.array([r[1] for r in other_ratings])
            
            # Calculate cosine similarity
            similarity = cosine_similarity([user_vector], [other_vector])[0][0]
            
            if similarity >= self.similarity_threshold:
                similar_users.append((other_user, similarity))
        
        similar_users.sort(key=lambda x: x[1], reverse=True)
        similar_users = similar_users[:limit]
        
        cache.set(cache_key, similar_users, 86400)
        return similar_users
    
    def get_collaborative_recommendations(self, user: CustomUser, limit: int = 10) -> List[Title]:
        """
        Recommend titles based on what similar users rated highly.
        """
        cache_key = f'collab_recommendations:{user.id}'
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        similar_users = self.find_similar_users(user)
        if not similar_users:
            return []
        
        # Get titles rated 8+ by similar users, not yet rated by user
        already_rated = set(Rating.objects.filter(user=user).values_list('title_id', flat=True))
        similar_user_ids = [u[0].id for u in similar_users]
        
        recommendations = Title.objects.filter(
            ratings__user_id__in=similar_user_ids,
            ratings__score__gte=8
        ).exclude(
            id__in=already_rated
        ).annotate(
            avg_similar_rating=models.Avg('ratings__score')
        ).distinct().order_by('-avg_similar_rating', '-rating_count')[:limit]
        
        recommendations_list = list(recommendations)
        cache.set(cache_key, recommendations_list, 86400)
        return recommendations_list
    
    # Hybrid Recommendation
    def get_hybrid_recommendations(self, user: CustomUser, limit: int = 10) -> List[Title]:
        """
        Combine content-based and collaborative filtering.
        """
        content_recs = self.get_content_based_recommendations(user, limit)
        collab_recs = self.get_collaborative_recommendations(user, limit)
        
        # Combine and remove duplicates, prioritizing collaborative
        seen = set()
        combined = []
        
        for title in collab_recs + content_recs:
            if title.id not in seen:
                combined.append(title)
                seen.add(title.id)
                if len(combined) >= limit:
                    break
        
        return combined[:limit]
    
    def update_recommendations_for_user(self, user: CustomUser):
        """
        Update recommendations in database for a user.
        """
        try:
            hybrid_recs = self.get_hybrid_recommendations(user, 50)
            
            # Clear old recommendations
            Recommendation.objects.filter(user=user).delete()
            
            # Create new recommendations
            for i, title in enumerate(hybrid_recs):
                confidence = max(0, 100 - (i * 2))  # Decrease confidence with position
                Recommendation.objects.create(
                    user=user,
                    title=title,
                    reason='collaborative' if i < len(self.find_similar_users(user)) else 'genre',
                    confidence_score=confidence
                )
            
            logger.info(f"Updated recommendations for user {user.id}")
        except Exception as e:
            logger.error(f"Error updating recommendations for user {user.id}: {e}")


from django.conf import settings
