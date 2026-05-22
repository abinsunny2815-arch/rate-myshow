"""
Celery tasks for background processing.
"""
from celery import shared_task
from django.core.cache import cache
from apps.recommendations.services import RecommendationEngine
from apps.ratings.models import RatingDistribution, Rating
from apps.titles.models import Title
import logging

logger = logging.getLogger(__name__)


@shared_task
def update_user_recommendations(user_id):
    """Update recommendations for a specific user."""
    try:
        from apps.users.models import CustomUser
        user = CustomUser.objects.get(id=user_id)
        engine = RecommendationEngine()
        engine.update_recommendations_for_user(user)
        logger.info(f"Updated recommendations for user {user_id}")
    except Exception as e:
        logger.error(f"Error updating recommendations for user {user_id}: {e}")


@shared_task
def update_rating_distributions():
    """Update rating distributions for all titles."""
    try:
        for title in Title.objects.all():
            rd, _ = RatingDistribution.objects.get_or_create(title=title)
            rd.update_distribution()
        logger.info("Updated all rating distributions")
    except Exception as e:
        logger.error(f"Error updating rating distributions: {e}")


@shared_task
def clear_expired_cache():
    """Clear expired cache entries."""
    try:
        cache.clear()
        logger.info("Cleared cache")
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")


@shared_task
def update_title_stats(title_id):
    """Update title statistics."""
    try:
        title = Title.objects.get(id=title_id)
        title.update_ratings()
        logger.info(f"Updated stats for title {title_id}")
    except Exception as e:
        logger.error(f"Error updating title stats: {e}")
