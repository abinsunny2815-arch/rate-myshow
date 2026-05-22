"""
Admin configuration for ratings app.
"""
from django.contrib import admin
from apps.ratings.models import Rating, Review, RatingDistribution


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'score', 'created_at']
    list_filter = ['score', 'created_at']
    search_fields = ['user__username', 'title__title']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'helpful_count', 'created_at']
    list_filter = ['contains_spoilers', 'created_at']
    search_fields = ['user__username', 'title__title', 'content']
    readonly_fields = ['helpful_count', 'unhelpful_count', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'


@admin.register(RatingDistribution)
class RatingDistributionAdmin(admin.ModelAdmin):
    list_display = ['title', 'updated_at']
    readonly_fields = ['updated_at']
