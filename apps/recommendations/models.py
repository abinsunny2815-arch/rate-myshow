"""
Models for recommendations app.
"""
from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MinValueValidator, MaxValueValidator


class Recommendation(models.Model):
    """Personalized recommendations for users."""
    REASON_CHOICES = [
        ('collaborative', 'Users like you watched this'),
        ('genre', 'Based on your favorite genres'),
        ('actor', 'Features actors you like'),
        ('trending', 'Trending this week'),
        ('similar', 'Similar to movies you rated highly'),
    ]
    
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='recommendations')
    title = models.ForeignKey('titles.Title', on_delete=models.CASCADE, related_name='recommended_to')
    
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    confidence_score = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    # Related items that influenced recommendation
    based_on_title = models.ForeignKey(
        'titles.Title',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='recommendations_based_on'
    )
    
    is_dismissed = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-confidence_score', '-created_at']
        unique_together = ('user', 'title', 'reason')
        indexes = [
            models.Index(fields=['user', '-confidence_score']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['-confidence_score']),
        ]
    
    def __str__(self):
        return f"Recommended {self.title.title} to {self.user.username}"


class SimilarTitle(models.Model):
    """Cache similar titles for quick retrieval."""
    title = models.OneToOneField('titles.Title', on_delete=models.CASCADE, related_name='similar_titles_cache')
    
    # Store IDs of similar titles (max 20)
    similar_omdb_ids = ArrayField(models.CharField(max_length=20), size=20, default=list)
    similarity_scores = ArrayField(models.FloatField(), size=20, default=list)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Similar Titles'
    
    def __str__(self):
        return f"Similar to {self.title.title}"


class CollaborativeRating(models.Model):
    """Store collaborative filtering ratings matrix."""
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='collaborative_ratings')
    title = models.ForeignKey('titles.Title', on_delete=models.CASCADE)
    
    # Average rating given by similar users
    predicted_rating = models.FloatField(null=True, blank=True)
    confidence = models.FloatField(default=0)  # 0-1, how confident we are
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'title')
        ordering = ['-confidence', '-updated_at']
    
    def __str__(self):
        return f"CF Rating: {self.user.username} - {self.title.title}"


class UserSimilarity(models.Model):
    """Similarity scores between users for collaborative filtering."""
    user1 = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='similarity_to')
    user2 = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='similar_users')
    
    similarity_score = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)])
    common_ratings = models.IntegerField(default=0)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user1', 'user2')
        ordering = ['-similarity_score']
    
    def __str__(self):
        return f"{self.user1.username} <-> {self.user2.username} ({self.similarity_score:.2f})"
