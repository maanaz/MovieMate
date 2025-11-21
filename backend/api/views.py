from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Avg, Count, Sum
from .models import (
    Content, Movie, TVShow, Genre, Platform,
    Rating, Review, WatchProgress, WatchHistory
)
from .serializers import (
    ContentSerializer, MovieSerializer, TVShowSerializer,
    GenreSerializer, PlatformSerializer, RatingSerializer,
    ReviewSerializer, WatchProgressSerializer, WatchHistorySerializer,
    ContentListSerializer
)
from .utils import (
    fetch_tmdb_movie, fetch_tmdb_tv, search_tmdb,
    get_recommendations_based_on_ratings, estimate_completion_time,
    generate_review_from_notes, search_omdb, fetch_omdb_title,
    update_recommendations_cache_after_import
)
from django.core.cache import cache


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    filter_backends = [SearchFilter]
    search_fields = ['name']


class PlatformViewSet(viewsets.ModelViewSet):
    queryset = Platform.objects.all()
    serializer_class = PlatformSerializer
    filter_backends = [SearchFilter]
    search_fields = ['name']


class ContentViewSet(viewsets.ModelViewSet):
    queryset = Content.objects.all()
    serializer_class = ContentSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'platform', 'content_type']
    search_fields = ['title', 'director', 'description']
    ordering_fields = ['title', 'release_date', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ContentListSerializer
        return ContentSerializer
    
    def get_queryset(self):
        queryset = Content.objects.all()
        
        # Filter by genre
        genre = self.request.query_params.get('genre', None)
        if genre:
            queryset = queryset.filter(genre__name__icontains=genre)
        
        # Filter by rating
        min_rating = self.request.query_params.get('min_rating', None)
        if min_rating:
            queryset = queryset.annotate(
                avg_rating=Avg('ratings__rating')
            ).filter(avg_rating__gte=min_rating)
        
        return queryset.distinct()

    def perform_create(self, serializer):
        instance = serializer.save()
        # Invalidate recommendations cache when new content is added
        try:
            cache.delete('recommendations_v2')
        except Exception:
            pass

    def perform_update(self, serializer):
        instance = serializer.save()
        # Invalidate recommendations cache when content is updated
        try:
            cache.delete('recommendations_v2')
        except Exception:
            pass
    
    @action(detail=False, methods=['get'])
    def movies(self, request):
        """Get all movies"""
        movies = self.queryset.filter(content_type='movie')
        serializer = ContentListSerializer(movies, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def tv_shows(self, request):
        """Get all TV shows"""
        tv_shows = self.queryset.filter(content_type='tv_show')
        serializer = ContentListSerializer(tv_shows, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get collection statistics"""
        total = self.queryset.count()
        movies = self.queryset.filter(content_type='movie').count()
        tv_shows = self.queryset.filter(content_type='tv_show').count()
        
        status_counts = {}
        for status_choice in Content.STATUS_CHOICES:
            status_counts[status_choice[0]] = self.queryset.filter(status=status_choice[0]).count()
        
        avg_rating = Rating.objects.aggregate(Avg('rating'))['rating__avg'] or 0
        
        return Response({
            'total': total,
            'movies': movies,
            'tv_shows': tv_shows,
            'status_counts': status_counts,
            'average_rating': round(avg_rating, 2),
        })
    
    @action(detail=True, methods=['get'])
    def completion_estimate(self, request, pk=None):
        """Get estimated completion time for a TV show"""
        content = self.get_object()
        result = estimate_completion_time(content)
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def recommendations(self, request):
        """Get content recommendations based on ratings"""
        # Return a larger pool (server-side) so frontend can display a slice and replacements are available
        recommendations = get_recommendations_based_on_ratings(pool_size=24)
        return Response(recommendations)
    
    @action(detail=False, methods=['get'])
    def search_tmdb(self, request):
        """Search TMDB API for movies/shows"""
        query = request.query_params.get('q', '')
        content_type = request.query_params.get('type', 'movie')
        
        if not query:
            return Response({'error': 'Query parameter "q" is required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        results = search_tmdb(query, content_type)
        return Response(results)
    
    @action(detail=False, methods=['post'])
    def import_from_tmdb(self, request):
        """Import content from TMDB"""
        tmdb_id = request.data.get('tmdb_id')
        content_type = request.data.get('content_type', 'movie')
        
        if not tmdb_id:
            return Response({'error': 'tmdb_id is required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Check if already exists
        if Content.objects.filter(tmdb_id=tmdb_id).exists():
            content = Content.objects.get(tmdb_id=tmdb_id)
            serializer = self.get_serializer(content)
            return Response({'message': 'Content already exists', 'data': serializer.data})
        
        # Fetch from TMDB
        if content_type == 'movie':
            data = fetch_tmdb_movie(tmdb_id)
            if not data:
                return Response({'error': 'Failed to fetch from TMDB'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            # Create genres
            genres = []
            for genre_name in data.get('genres', []):
                genre, _ = Genre.objects.get_or_create(name=genre_name)
                genres.append(genre)
            
            # Allow client to specify desired initial status (e.g., 'completed')
            status_val = request.data.get('status') or 'wishlist'
            movie = Movie.objects.create(
                title=data['title'],
                description=data.get('description', ''),
                release_date=data.get('release_date') or None,
                poster_url=data.get('poster_url', ''),
                runtime=data.get('runtime'),
                tmdb_id=tmdb_id,
                imdb_id=data.get('imdb_id') or '',
                director=data.get('director') or '',
                content_type='movie',
                status=status_val,
            )
            movie.genre.set(genres)
            
            # Update recommendations cache to remove this imported item and replace it
            try:
                update_recommendations_cache_after_import(genres=[g.name for g in genres], new_tmdb_id=tmdb_id, new_local_id=movie.id, pool_size=24)
            except Exception:
                try:
                    cache.delete('recommendations_v2_24')
                except Exception:
                    pass

            serializer = MovieSerializer(movie)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        else:  # TV show
            data = fetch_tmdb_tv(tmdb_id)
            if not data:
                return Response({'error': 'Failed to fetch from TMDB'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            # Create genres
            genres = []
            for genre_name in data.get('genres', []):
                genre, _ = Genre.objects.get_or_create(name=genre_name)
                genres.append(genre)
            
            status_val = request.data.get('status') or 'wishlist'
            tv_show = TVShow.objects.create(
                title=data['title'],
                description=data.get('description', ''),
                release_date=data.get('release_date') or None,
                poster_url=data.get('poster_url', ''),
                total_seasons=data.get('total_seasons', 1),
                total_episodes=data.get('total_episodes', 0),
                episodes_per_season=data.get('episodes_per_season', {}),
                tmdb_id=tmdb_id,
                imdb_id=data.get('imdb_id') or '',
                director=data.get('director') or '',
                content_type='tv_show',
                status=status_val,
            )
            tv_show.genre.set(genres)
            
            # Update recommendations cache to remove this imported item and replace it
            try:
                update_recommendations_cache_after_import(genres=[g.name for g in genres], new_tmdb_id=tmdb_id, new_local_id=tv_show.id, pool_size=24)
            except Exception:
                try:
                    cache.delete('recommendations_v2_24')
                except Exception:
                    pass

            serializer = TVShowSerializer(tv_show)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def search_omdb(self, request):
        """Search OMDB API for movies/shows"""
        query = request.query_params.get('q', '')
        content_type = request.query_params.get('type', 'movie')

        if not query:
            return Response({'error': 'Query parameter "q" is required'},
                            status=status.HTTP_400_BAD_REQUEST)

        results = search_omdb(query, content_type)
        return Response(results)

    @action(detail=False, methods=['post'])
    def import_from_omdb(self, request):
        """Import content from OMDB"""
        imdb_id = request.data.get('imdb_id')

        if not imdb_id:
            return Response({'error': 'imdb_id is required'},
                            status=status.HTTP_400_BAD_REQUEST)

        existing_content = Content.objects.filter(imdb_id__iexact=imdb_id).first()
        if existing_content:
            serializer = self.get_serializer(existing_content)
            return Response({'message': 'Content already exists', 'data': serializer.data})

        data = fetch_omdb_title(imdb_id)
        if not data:
            return Response({'error': 'Failed to fetch from OMDB'},
                            status=status.HTTP_400_BAD_REQUEST)

        genres = []
        for genre_name in data.get('genres', []):
            genre, _ = Genre.objects.get_or_create(name=genre_name)
            genres.append(genre)

        content_type = data.get('content_type', 'movie')

        if content_type == 'movie':
            movie = Movie.objects.create(
                title=data['title'],
                description=data.get('description', ''),
                release_date=data.get('release_date') or None,
                poster_url=data.get('poster_url', ''),
                runtime=data.get('runtime'),
                imdb_id=data.get('imdb_id'),
                content_type='movie',
                status='wishlist',
            )
            movie.genre.set(genres)
            try:
                update_recommendations_cache_after_import(genres=[g.name for g in genres], new_tmdb_id=None, new_local_id=movie.id, pool_size=24)
            except Exception:
                try:
                    cache.delete('recommendations_v2_24')
                except Exception:
                    pass
            serializer = MovieSerializer(movie)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        tv_show = TVShow.objects.create(
            title=data['title'],
            description=data.get('description', ''),
            release_date=data.get('release_date') or None,
            poster_url=data.get('poster_url', ''),
            total_seasons=data.get('total_seasons') or 1,
            total_episodes=data.get('total_episodes') or 0,
            episodes_per_season={},
            imdb_id=data.get('imdb_id'),
            content_type='tv_show',
            status='wishlist',
        )
        tv_show.genre.set(genres)
        try:
            update_recommendations_cache_after_import(genres=[g.name for g in genres], new_tmdb_id=None, new_local_id=tv_show.id, pool_size=24)
        except Exception:
            try:
                cache.delete('recommendations_v2_24')
            except Exception:
                pass
        serializer = TVShowSerializer(tv_show)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class RatingViewSet(viewsets.ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['content', 'rating']
    ordering_fields = ['rated_at']
    ordering = ['-rated_at']
    
    def perform_create(self, serializer):
        # Update or create rating for content
        content_id = self.request.data.get('content')
        rating_value = self.request.data.get('rating')
        
        if content_id:
            rating, created = Rating.objects.update_or_create(
                content_id=content_id,
                defaults={'rating': rating_value}
            )
        else:
            serializer.save()


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['content']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    @action(detail=False, methods=['post'])
    def generate_from_notes(self, request):
        """Generate review from notes"""
        notes = request.data.get('notes', '')
        content_id = request.data.get('content')
        
        if not notes or not content_id:
            return Response({'error': 'notes and content are required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        review_text = generate_review_from_notes(notes)
        
        review, created = Review.objects.update_or_create(
            content_id=content_id,
            defaults={
                'review_text': review_text,
                'notes': notes
            }
        )
        
        serializer = ReviewSerializer(review)
        return Response(serializer.data)


class WatchProgressViewSet(viewsets.ModelViewSet):
    queryset = WatchProgress.objects.all()
    serializer_class = WatchProgressSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['content', 'completed']
    ordering_fields = ['watched_at']
    ordering = ['-watched_at']
    
    @action(detail=False, methods=['post'])
    def mark_episode(self, request):
        """Mark an episode as watched"""
        content_id = request.data.get('content')
        season = request.data.get('season', 1)
        episode = request.data.get('episode', 1)
        watch_time = request.data.get('watch_time_minutes')
        
        if not content_id:
            return Response({'error': 'content is required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        progress, created = WatchProgress.objects.update_or_create(
            content_id=content_id,
            season=season,
            episode=episode,
            defaults={
                'completed': True,
                'watch_time_minutes': watch_time
            }
        )
        
        # Create watch history entry
        content = Content.objects.get(id=content_id)
        WatchHistory.objects.create(
            content=content,
            watch_time_minutes=watch_time or 45,
            session_type='episode'
        )
        
        serializer = WatchProgressSerializer(progress)
        return Response(serializer.data)


class WatchHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = WatchHistory.objects.all()
    serializer_class = WatchHistorySerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['content', 'watch_date', 'session_type']
    ordering_fields = ['watch_date']
    ordering = ['-watch_date']
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get watch time statistics"""
        from django.utils import timezone
        from datetime import timedelta
        
        # Weekly stats
        week_ago = timezone.now().date() - timedelta(days=7)
        weekly_time = WatchHistory.objects.filter(
            watch_date__gte=week_ago
        ).aggregate(total=Sum('watch_time_minutes'))['total'] or 0
        
        # Monthly stats
        month_ago = timezone.now().date() - timedelta(days=30)
        monthly_time = WatchHistory.objects.filter(
            watch_date__gte=month_ago
        ).aggregate(total=Sum('watch_time_minutes'))['total'] or 0
        
        # Daily breakdown for last 7 days
        daily_stats = []
        for i in range(7):
            date = timezone.now().date() - timedelta(days=i)
            day_time = WatchHistory.objects.filter(
                watch_date=date
            ).aggregate(total=Sum('watch_time_minutes'))['total'] or 0
            daily_stats.append({
                'date': date.isoformat(),
                'minutes': day_time
            })
        
        return Response({
            'weekly_minutes': weekly_time,
            'monthly_minutes': monthly_time,
            'weekly_hours': round(weekly_time / 60, 1),
            'monthly_hours': round(monthly_time / 60, 1),
            'daily_breakdown': list(reversed(daily_stats))
        })


# Need to import Sum for statistics
from django.db.models import Sum

