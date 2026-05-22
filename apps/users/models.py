"""
Models for users app.
"""
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify


class CustomUser(AbstractUser):
    """Extended user model with profile information."""
    THEME_CHOICES = [
        ('dark', 'Dark Mode'),
        ('light', 'Light Mode'),
        ('auto', 'Auto (System)'),
    ]
    
    email = models.EmailField(unique=True)
    bio = models.TextField(blank=True, max_length=500)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    theme_preference = models.CharField(max_length=10, choices=THEME_CHOICES, default='dark')
    
    # Stats
    total_ratings = models.IntegerField(default=0)
    total_reviews = models.IntegerField(default=0)
    watchlist_count = models.IntegerField(default=0)
    
    # Privacy
    is_public = models.BooleanField(default=True, help_text="Make profile visible to other users")
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_activity = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['email']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_full_name() or self.username}"
    
    @property
    def display_name(self):
        """Return full name if available, otherwise username."""
        return self.get_full_name() or self.username
    
    def update_stats(self):
        """Update user statistics."""
        from apps.ratings.models import Rating, Review
        from apps.titles.models import Watchlist
        
        self.total_ratings = Rating.objects.filter(user=self).count()
        self.total_reviews = Review.objects.filter(user=self).count()
        self.watchlist_count = Watchlist.objects.filter(user=self).count()
        self.save(update_fields=['total_ratings', 'total_reviews', 'watchlist_count'])


class UserActivity(models.Model):
    """Track user activities for recommendations."""
    ACTIVITY_CHOICES = [
        ('rating', 'Rating Added'),
        ('review', 'Review Written'),
        ('watchlist', 'Added to Watchlist'),
        ('viewed', 'Viewed Title'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_CHOICES)
    title_id = models.CharField(max_length=20)  # OMDB ID
    title_name = models.CharField(max_length=500)
    rating_given = models.FloatField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(10)])
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'User Activities'
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['title_id']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.get_activity_type_display()}"
