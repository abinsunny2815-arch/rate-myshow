"""
Admin configuration for titles app.
"""
from django.contrib import admin
from apps.titles.models import Title, Genre, Actor, Person, Watchlist


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = ['title', 'type', 'year', 'avg_rating', 'rating_count']
    list_filter = ['type', 'year', 'created_at']
    search_fields = ['title', 'omdb_id', 'plot']
    readonly_fields = ['omdb_id', 'created_at', 'updated_at', 'last_synced', 'avg_rating', 'rating_count']
    filter_horizontal = ['genres', 'actors', 'directors']
    date_hierarchy = 'created_at'


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


@admin.register(Actor)
class ActorAdmin(admin.ModelAdmin):
    list_display = ['name', 'born_year']
    search_fields = ['name']


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ['name', 'role']
    search_fields = ['name', 'role']


@admin.register(Watchlist)
class WatchlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'status', 'added_at']
    list_filter = ['status', 'added_at']
    search_fields = ['user__username', 'title__title']
    readonly_fields = ['added_at', 'updated_at']
    date_hierarchy = 'added_at'
