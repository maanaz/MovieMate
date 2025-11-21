from django.db import models
from django.utils import timezone


class Genre(models.Model):
    """Genre model for categorizing movies and shows"""
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name


class Platform(models.Model):
    """Platform model for streaming services"""
    name = models.CharField(max_length=100, unique=True)
    icon = models.CharField(max_length=50, blank=True)  # For emoji icons
    
    def __str__(self):
        return self.name


class Content(models.Model):
    """Base model for movies and TV shows"""
    STATUS_CHOICES = [
        ('watching', 'Watching'),
        ('completed', 'Completed'),
        ('wishlist', 'Wishlist'),
        ('paused', 'Paused'),
    ]
    
    CONTENT_TYPE_CHOICES = [
        ('movie', 'Movie'),
        ('tv_show', 'TV Show'),
    ]
    
    title = models.CharField(max_length=200)
    director = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    release_date = models.DateField(null=True, blank=True)
    genre = models.ManyToManyField(Genre, blank=True)
    platform = models.ForeignKey(Platform, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='wishlist')
    content_type = models.CharField(max_length=10, choices=CONTENT_TYPE_CHOICES)
    poster_url = models.URLField(blank=True)
    tmdb_id = models.IntegerField(null=True, blank=True, unique=True)
    imdb_id = models.CharField(max_length=20, blank=True)
    runtime = models.IntegerField(null=True, blank=True, help_text="Runtime in minutes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


class TVShow(Content):
    """TV Show specific model"""
    total_seasons = models.IntegerField(default=1)
    total_episodes = models.IntegerField(default=0)
    episodes_per_season = models.JSONField(default=dict, blank=True, 
                                           help_text="Dictionary with season number as key and episode count as value")
    
    class Meta:
        verbose_name = "TV Show"
        verbose_name_plural = "TV Shows"


class Movie(Content):
    """Movie specific model"""
    pass
    
    class Meta:
        verbose_name = "Movie"
        verbose_name_plural = "Movies"


class WatchProgress(models.Model):
    """Track watching progress for TV shows"""
    content = models.ForeignKey(Content, on_delete=models.CASCADE, related_name='watch_progress')
    season = models.IntegerField(default=1)
    episode = models.IntegerField(default=0)
    completed = models.BooleanField(default=False)
    watched_at = models.DateTimeField(default=timezone.now)
    watch_time_minutes = models.IntegerField(null=True, blank=True, 
                                             help_text="Time spent watching in minutes")
    
    class Meta:
        ordering = ['-watched_at']
        unique_together = ['content', 'season', 'episode']
    
    def __str__(self):
        return f"{self.content.title} - S{self.season}E{self.episode}"


class Rating(models.Model):
    """Rating model for movies and shows"""
    content = models.ForeignKey(Content, on_delete=models.CASCADE, related_name='ratings')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 11)], 
                                 help_text="Rating from 1 to 10")
    rated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-rated_at']
        unique_together = ['content']
    
    def __str__(self):
        return f"{self.content.title} - {self.rating}/10"


class Review(models.Model):
    """Review model for movies and shows"""
    content = models.ForeignKey(Content, on_delete=models.CASCADE, related_name='reviews')
    review_text = models.TextField()
    notes = models.TextField(blank=True, help_text="Personal notes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Review for {self.content.title}"


class WatchHistory(models.Model):
    """Track watch sessions for statistics"""
    content = models.ForeignKey(Content, on_delete=models.CASCADE, related_name='watch_history')
    watch_date = models.DateField(default=timezone.now)
    watch_time_minutes = models.IntegerField(help_text="Time spent watching in minutes")
    session_type = models.CharField(max_length=20, choices=[
        ('movie', 'Movie'),
        ('episode', 'Episode'),
        ('binge', 'Binge Watch'),
    ], default='episode')
    
    class Meta:
        ordering = ['-watch_date']
    
    def __str__(self):
        return f"{self.content.title} - {self.watch_date}"


