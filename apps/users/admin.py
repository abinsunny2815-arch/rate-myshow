"""
Admin configuration for users app.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from apps.users.models import CustomUser, UserActivity


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'total_ratings', 'total_reviews', 'created_at']
    list_filter = ['created_at', 'theme_preference', 'is_public', 'is_staff']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    readonly_fields = ['total_ratings', 'total_reviews', 'watchlist_count', 'created_at', 'updated_at', 'last_activity']
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'bio', 'avatar')}),
        ('Preferences', {'fields': ('theme_preference', 'is_public')}),
        ('Statistics', {'fields': ('total_ratings', 'total_reviews', 'watchlist_count')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined', 'created_at', 'updated_at', 'last_activity')}),
    )
    
    date_hierarchy = 'created_at'


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ['user', 'activity_type', 'title_name', 'rating_given', 'created_at']
    list_filter = ['activity_type', 'created_at']
    search_fields = ['user__username', 'title_name']
    readonly_fields = ['created_at', 'user', 'activity_type']
    date_hierarchy = 'created_at'
