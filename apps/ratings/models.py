"""
Models for ratings app.
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse


class Rating(models.Model):
    """User ratings for titles."""
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='ratings')
    title = models.ForeignKey('titles.Title', on_delete=models.CASCADE, related_name='ratings')
    
    score = models.FloatField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Rating from 1 to 10 (supports 0.5 increments)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'title')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['title', '-created_at']),
            models.Index(fields=['score']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.title.title} ({self.score}/10)"


class Review(models.Model):
    """User reviews for titles."""
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='reviews')
    title = models.ForeignKey('titles.Title', on_delete=models.CASCADE, related_name='reviews')
    rating = models.OneToOneField(Rating, on_delete=models.SET_NULL, null=True, blank=True, related_name='review')
    
    title_review = models.CharField(max_length=300, blank=True)
    content = models.TextField()
    contains_spoilers = models.BooleanField(default=False)
    
    helpful_count = models.IntegerField(default=0)
    unhelpful_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'title')
        ordering = ['-helpful_count', '-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['title', '-created_at']),
            models.Index(fields=['contains_spoilers']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - Review of {self.title.title}"
    
    def get_absolute_url(self):
        return reverse('review_detail', kwargs={'pk': self.pk})
    
    @property
    def helpful_ratio(self):
        """Calculate helpful ratio."""
        total = self.helpful_count + self.unhelpful_count
        if total == 0:
            return 0
        return (self.helpful_count / total) * 100


class RatingDistribution(models.Model):
    """Cache rating distribution for each title."""
    title = models.OneToOneField('titles.Title', on_delete=models.CASCADE, related_name='rating_distribution')
    
    # Count of ratings per score
    count_10 = models.IntegerField(default=0)
    count_9 = models.IntegerField(default=0)
    count_8 = models.IntegerField(default=0)
    count_7 = models.IntegerField(default=0)
    count_6 = models.IntegerField(default=0)
    count_5 = models.IntegerField(default=0)
    count_4 = models.IntegerField(default=0)
    count_3 = models.IntegerField(default=0)
    count_2 = models.IntegerField(default=0)
    count_1 = models.IntegerField(default=0)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Rating Distributions'
    
    def __str__(self):
        return f"Rating Distribution for {self.title.title}"
    
    def update_distribution(self):
        """Update rating distribution from Rating objects."""
        from apps.ratings.models import Rating
        
        # Reset counters
        self.count_10 = 0
        self.count_9 = 0
        self.count_8 = 0
        self.count_7 = 0
        self.count_6 = 0
        self.count_5 = 0
        self.count_4 = 0
        self.count_3 = 0
        self.count_2 = 0
        self.count_1 = 0
        
        # Count ratings
        ratings = Rating.objects.filter(title=self.title)
        for rating in ratings:
            score = int(rating.score)
            field_name = f'count_{score}'
            if hasattr(self, field_name):
                setattr(self, field_name, getattr(self, field_name) + 1)
        
        self.save()
    
    def get_distribution_dict(self):
        """Return distribution as dictionary."""
        return {
            10: self.count_10,
            9: self.count_9,
            8: self.count_8,
            7: self.count_7,
            6: self.count_6,
            5: self.count_5,
            4: self.count_4,
            3: self.count_3,
            2: self.count_2,
            1: self.count_1,
        }
