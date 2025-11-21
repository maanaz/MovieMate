from django.contrib import admin
from .models import Content, Movie, TVShow, Genre, Platform, Rating, Review, WatchProgress, WatchHistory


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Platform)
class PlatformAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon']
    search_fields = ['name']


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ['title', 'director', 'status', 'platform', 'release_date']
    list_filter = ['status', 'platform', 'genre']
    search_fields = ['title', 'director']
    filter_horizontal = ['genre']


@admin.register(TVShow)
class TVShowAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'platform', 'total_seasons', 'total_episodes']
    list_filter = ['status', 'platform', 'genre']
    search_fields = ['title']
    filter_horizontal = ['genre']


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ['content', 'rating', 'rated_at']
    list_filter = ['rating', 'rated_at']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['content', 'created_at', 'updated_at']
    search_fields = ['review_text', 'notes']


@admin.register(WatchProgress)
class WatchProgressAdmin(admin.ModelAdmin):
    list_display = ['content', 'season', 'episode', 'completed', 'watched_at']
    list_filter = ['completed', 'watched_at']


@admin.register(WatchHistory)
class WatchHistoryAdmin(admin.ModelAdmin):
    list_display = ['content', 'watch_date', 'watch_time_minutes', 'session_type']
    list_filter = ['watch_date', 'session_type']


