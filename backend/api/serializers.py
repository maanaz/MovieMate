from rest_framework import serializers
from .models import (
    Content, Movie, TVShow, Genre, Platform, 
    Rating, Review, WatchProgress, WatchHistory
)


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'name']


class PlatformSerializer(serializers.ModelSerializer):
    class Meta:
        model = Platform
        fields = ['id', 'name', 'icon']


class ContentSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True, read_only=True)
    genre_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Genre.objects.all(), write_only=True, required=False, source='genre'
    )
    platform_name = serializers.CharField(source='platform.name', read_only=True)
    rating_value = serializers.SerializerMethodField()
    review_text = serializers.SerializerMethodField()
    progress_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Content
        fields = [
            'id', 'title', 'director', 'description', 'release_date',
            'genre', 'genre_ids', 'platform', 'platform_name', 'status',
            'content_type', 'poster_url', 'tmdb_id', 'imdb_id', 'runtime',
            'rating_value', 'review_text', 'progress_info',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_rating_value(self, obj):
        rating = obj.ratings.first()
        return rating.rating if rating else None
    
    def get_review_text(self, obj):
        review = obj.reviews.first()
        return review.review_text if review else None
    
    def get_progress_info(self, obj):
        if obj.content_type == 'tv_show':
            progress = obj.watch_progress.all()
            total_watched = progress.filter(completed=True).count()
            latest = progress.order_by('-watched_at').first()
            return {
                'total_watched_episodes': total_watched,
                'latest_season': latest.season if latest else None,
                'latest_episode': latest.episode if latest else None,
            }
        return None


class MovieSerializer(ContentSerializer):
    class Meta(ContentSerializer.Meta):
        model = Movie


class TVShowSerializer(ContentSerializer):
    total_seasons = serializers.IntegerField()
    total_episodes = serializers.IntegerField()
    episodes_per_season = serializers.JSONField()
    
    class Meta(ContentSerializer.Meta):
        model = TVShow
        fields = ContentSerializer.Meta.fields + [
            'total_seasons', 'total_episodes', 'episodes_per_season'
        ]


class RatingSerializer(serializers.ModelSerializer):
    content_title = serializers.CharField(source='content.title', read_only=True)
    
    class Meta:
        model = Rating
        fields = ['id', 'content', 'content_title', 'rating', 'rated_at']
        read_only_fields = ['rated_at']
        # We handle uniqueness (one rating per content) in the view's perform_create
        # so disable the default UniqueTogetherValidator added by DRF for the model.
        validators = []


class ReviewSerializer(serializers.ModelSerializer):
    content_title = serializers.CharField(source='content.title', read_only=True)
    
    class Meta:
        model = Review
        fields = ['id', 'content', 'content_title', 'review_text', 'notes', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class WatchProgressSerializer(serializers.ModelSerializer):
    content_title = serializers.CharField(source='content.title', read_only=True)
    
    class Meta:
        model = WatchProgress
        fields = [
            'id', 'content', 'content_title', 'season', 'episode',
            'completed', 'watched_at', 'watch_time_minutes'
        ]


class WatchHistorySerializer(serializers.ModelSerializer):
    content_title = serializers.CharField(source='content.title', read_only=True)
    
    class Meta:
        model = WatchHistory
        fields = ['id', 'content', 'content_title', 'watch_date', 'watch_time_minutes', 'session_type']
        read_only_fields = []


class ContentListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views"""
    genre = GenreSerializer(many=True, read_only=True)
    platform_name = serializers.CharField(source='platform.name', read_only=True)
    rating_value = serializers.SerializerMethodField()
    
    class Meta:
        model = Content
        fields = [
            'id', 'title', 'director', 'release_date', 'genre',
            'platform_name', 'status', 'content_type', 'poster_url',
            'rating_value', 'runtime'
        ]
    
    def get_rating_value(self, obj):
        rating = obj.ratings.first()
        return rating.rating if rating else None


