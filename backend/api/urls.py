from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ContentViewSet, GenreViewSet, PlatformViewSet,
    RatingViewSet, ReviewViewSet, WatchProgressViewSet,
    WatchHistoryViewSet
)

router = DefaultRouter()
router.register(r'content', ContentViewSet, basename='content')
router.register(r'genres', GenreViewSet, basename='genre')
router.register(r'platforms', PlatformViewSet, basename='platform')
router.register(r'ratings', RatingViewSet, basename='rating')
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'watch-progress', WatchProgressViewSet, basename='watch-progress')
router.register(r'watch-history', WatchHistoryViewSet, basename='watch-history')

urlpatterns = [
    path('', include(router.urls)),
]


