"""
Models for titles app - continued admin and helpers.
"""
from django.contrib import admin


# Admin classes are in admin.py
# This file can be used for signal handlers and other helpers

from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.ratings.models import Rating, RatingDistribution
from apps.users.models import UserActivity, CustomUser


@receiver(post_save, sender=Rating)
def on_rating_created(sender, instance, created, **kwargs):
    """Update title stats and user activity when rating created."""
    from apps.titles.models import Title
    from rateMySh.tasks import update_title_stats
    from django.utils import timezone
    
    # Update title stats
    instance.title.update_ratings()
    
    # Update rating distribution
    rd, _ = RatingDistribution.objects.get_or_create(title=instance.title)
    rd.update_distribution()
    
    # Record user activity
    UserActivity.objects.create(
        user=instance.user,
        activity_type='rating',
        title_id=instance.title.omdb_id,
        title_name=instance.title.title,
        rating_given=instance.score
    )
    
    # Update user stats
    instance.user.update_stats()
    
    # Trigger recommendations update asynchronously
    try:
        update_title_stats.delay(instance.title.id)
    except:
        pass  # Celery might not be running


@receiver(post_save, sender=UserActivity)
def on_user_activity(sender, instance, created, **kwargs):
    """Update user last activity on any activity."""
    if created:
        instance.user.last_activity = __import__('django.utils', fromlist=['timezone']).timezone.now()
        instance.user.save(update_fields=['last_activity'])
