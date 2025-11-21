"""
URL configuration for moviemate project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse

def api_root(request):
    """Root API endpoint info"""
    return JsonResponse({
        'message': 'MovieMate API',
        'version': '1.0',
        'endpoints': {
            'admin': '/admin/',
            'api': '/api/',
            'content': '/api/content/',
            'movies': '/api/content/movies/',
            'tv_shows': '/api/content/tv_shows/',
            'genres': '/api/genres/',
            'platforms': '/api/platforms/',
            'ratings': '/api/ratings/',
            'reviews': '/api/reviews/',
            'watch_progress': '/api/watch-progress/',
            'watch_history': '/api/watch-history/',
            'statistics': '/api/content/statistics/',
            'recommendations': '/api/content/recommendations/',
        },
        'frontend': 'http://localhost:3000' if settings.DEBUG else 'Production URL'
    })

urlpatterns = [
    path('', api_root, name='api-root'),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

