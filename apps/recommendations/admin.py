"""
Admin configuration for recommendations app.
"""
from django.contrib import admin
from apps.recommendations.models import Recommendation, SimilarTitle, CollaborativeRating


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'reason', 'confidence_score', 'created_at']
    list_filter = ['reason', 'created_at', 'is_dismissed']
    search_fields = ['user__username', 'title__title']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'


@admin.register(SimilarTitle)
class SimilarTitleAdmin(admin.ModelAdmin):
    list_display = ['title', 'updated_at']
    readonly_fields = ['updated_at']


@admin.register(CollaborativeRating)
class CollaborativeRatingAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'predicted_rating', 'confidence']
    list_filter = ['updated_at']
    search_fields = ['user__username', 'title__title']
    readonly_fields = ['updated_at']
