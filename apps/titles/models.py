"""
Models for titles app - movies and TV shows.
"""
from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
import json


class Title(models.Model):
    """Store movie and TV show data from OMDB."""
    TYPE_CHOICES = [
        ('movie', 'Movie'),
        ('series', 'TV Series'),
        ('episode', 'Episode'),
    ]
    
    omdb_id = models.CharField(max_length=20, unique=True, db_index=True)  # tt1234567
    title = models.CharField(max_length=500, db_index=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    year = models.IntegerField(null=True, blank=True)
    released_date = models.DateField(null=True, blank=True)
    
    # Basic info
    rated = models.CharField(max_length=20, blank=True)  # PG, R, etc.
    runtime = models.IntegerField(null=True, blank=True, help_text="Runtime in minutes")
    plot = models.TextField(blank=True)
    poster_url = models.URLField(blank=True)
    
    # Ratings & scores
    imdb_rating = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(10)])
    imdb_votes = models.IntegerField(default=0)
    
    # Site-specific aggregates
    avg_rating = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])
    rating_count = models.IntegerField(default=0)
    
    # Collections
    genres = models.ManyToManyField('Genre', related_name='titles', blank=True)
    actors = models.ManyToManyField('Actor', related_name='titles', blank=True)
    directors = models.ManyToManyField('Person', related_name='directed_titles', blank=True)
    
    # Meta
    director = models.CharField(max_length=500, blank=True)
    writer = models.CharField(max_length=500, blank=True)
    production = models.CharField(max_length=500, blank=True)
    country = models.CharField(max_length=200, blank=True)
    language = models.CharField(max_length=200, blank=True)
    
    # Raw OMDB data (backup)
    omdb_data = models.JSONField(default=dict, blank=True)
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_synced = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-imdb_rating', '-rating_count']
        verbose_name = 'Title'
        verbose_name_plural = 'Titles'
        indexes = [
            models.Index(fields=['omdb_id']),
            models.Index(fields=['title']),
            models.Index(fields=['type']),
            models.Index(fields=['-avg_rating']),
            models.Index(fields=['-rating_count']),
        ]
    
    def __str__(self):
        year_str = f" ({self.year})" if self.year else ""
        return f"{self.title}{year_str}"
    
    def get_absolute_url(self):
        return reverse('title_detail', kwargs={'omdb_id': self.omdb_id})
    
    @property
    def is_movie(self):
        return self.type == 'movie'
    
    @property
    def is_series(self):
        return self.type == 'series'
    
    def update_ratings(self):
        """Update average rating and count."""
        from apps.ratings.models import Rating
        ratings = Rating.objects.filter(title=self)
        if ratings.exists():
            self.rating_count = ratings.count()
            self.avg_rating = ratings.aggregate(models.Avg('score'))['score__avg'] or 0
            self.save(update_fields=['avg_rating', 'rating_count'])


class Genre(models.Model):
    """Movie/TV genres."""
    name = models.CharField(max_length=100, unique=True, db_index=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('genre_list', kwargs={'slug': self.slug})


class Actor(models.Model):
    """Actor information."""
    name = models.CharField(max_length=300, unique=True, db_index=True)
    bio = models.TextField(blank=True)
    image_url = models.URLField(blank=True)
    born_year = models.IntegerField(null=True, blank=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Actor'
        verbose_name_plural = 'Actors'
    
    def __str__(self):
        return self.name


class Person(models.Model):
    """Directors, writers, producers."""
    name = models.CharField(max_length=300, unique=True, db_index=True)
    role = models.CharField(max_length=50, blank=True)  # Director, Writer, Producer
    bio = models.TextField(blank=True)
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'People'
    
    def __str__(self):
        return self.name


class Watchlist(models.Model):
    """User watchlist for titles."""
    STATUS_CHOICES = [
        ('to-watch', 'To Watch'),
        ('watching', 'Watching'),
        ('completed', 'Completed'),
        ('dropped', 'Dropped'),
    ]
    
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='watchlists')
    title = models.ForeignKey(Title, on_delete=models.CASCADE, related_name='watchlist_entries')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='to-watch')
    priority = models.IntegerField(default=0, help_text="0=Low, 1=Medium, 2=High")
    notes = models.TextField(blank=True)
    
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'title')
        ordering = ['-priority', '-added_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['user', '-added_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.title.title} ({self.status})"
