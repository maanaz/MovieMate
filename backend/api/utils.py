"""
Utility functions for TMDB API integration and recommendations
"""
import requests
from django.conf import settings
from django.core.cache import cache
from datetime import datetime
from typing import Dict, Optional, List
from .models import Content, Rating, Genre, TVShow, WatchHistory, WatchProgress
def fetch_tmdb_movie(tmdb_id: int) -> Optional[Dict]:
    """Fetch movie details from TMDB API"""
    api_key = settings.TMDB_API_KEY
    if not api_key:
        return None
    cache_key = f"tmdb_movie_{tmdb_id}"
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}"
    params = {
        'api_key': api_key,
        'language': 'en-US'
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        poster_path = data.get('poster_path') or ''
        result = {
            'title': data.get('title'),
            'description': data.get('overview') or '',
            'release_date': data.get('release_date'),
            'poster_url': f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else '',
            'runtime': data.get('runtime') or 0,
            'imdb_id': None,
            'genres': [g['name'] for g in data.get('genres', [])],
            'director': None,
        }

        # Try to fetch director from credits and IMDB id from external_ids
        try:
            credits_url = f"https://api.themoviedb.org/3/movie/{tmdb_id}/credits"
            credits_resp = requests.get(credits_url, params={'api_key': api_key}, timeout=10)
            credits_resp.raise_for_status()
            credits = credits_resp.json()
            for member in credits.get('crew', []):
                if member.get('job') == 'Director':
                    result['director'] = member.get('name')
                    break

            ext_url = f"https://api.themoviedb.org/3/movie/{tmdb_id}/external_ids"
            ext_resp = requests.get(ext_url, params={'api_key': api_key}, timeout=10)
            ext_resp.raise_for_status()
            ext = ext_resp.json()
            if ext.get('imdb_id'):
                result['imdb_id'] = ext.get('imdb_id')
        except Exception:
            # Non-fatal if credits/external ids fail
            pass

        # Cache movie details for 24 hours
        cache.set(cache_key, result, 60 * 60 * 24)
        return result
    except Exception as e:
        print(f"Error fetching TMDB movie: {e}")
        return None


def fetch_tmdb_tv(tmdb_id: int) -> Optional[Dict]:
    """Fetch TV show details from TMDB API"""
    api_key = settings.TMDB_API_KEY
    if not api_key:
        return None
    cache_key = f"tmdb_tv_{tmdb_id}"
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    url = f"https://api.themoviedb.org/3/tv/{tmdb_id}"
    params = {
        'api_key': api_key,
        'language': 'en-US'
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Get episode counts per season
        episodes_per_season = {}
        for season in data.get('seasons', []):
            episodes_per_season[season['season_number']] = season['episode_count']
        
        poster_path = data.get('poster_path') or ''
        result = {
            'title': data.get('name'),
            'description': data.get('overview') or '',
            'release_date': data.get('first_air_date'),
            'poster_url': f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else '',
            'total_seasons': data.get('number_of_seasons', 0),
            'total_episodes': data.get('number_of_episodes', 0),
            'episodes_per_season': episodes_per_season,
            'genres': [g['name'] for g in data.get('genres', [])],
        }
        # Cache TV details for 24 hours
        cache.set(cache_key, result, 60 * 60 * 24)
        return result
    except Exception as e:
        print(f"Error fetching TMDB TV show: {e}")
        return None


def search_tmdb(query: str, content_type: str = 'movie') -> List[Dict]:
    """Search TMDB for movies or TV shows"""
    api_key = settings.TMDB_API_KEY
    if not api_key:
        return []
    
    search_type = 'movie' if content_type == 'movie' else 'tv'
    url = f"https://api.themoviedb.org/3/search/{search_type}"
    params = {
        'api_key': api_key,
        'language': 'en-US',
        'query': query,
        'page': 1
    }
    
    cache_key = f"tmdb_search_{content_type}_{query.strip().lower()}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        results = []
        for item in data.get('results', [])[:10]:  # Limit to top 10
            tmdb_id = item.get('id')
            base_result = {
                'tmdb_id': tmdb_id,
                'title': item.get('title') if content_type == 'movie' else item.get('name'),
                'description': item.get('overview') or '',
                'release_date': item.get('release_date') if content_type == 'movie' else item.get('first_air_date'),
                'poster_url': f"https://image.tmdb.org/t/p/w500{item.get('poster_path', '')}" if item.get('poster_path') else '',
            }

            # Enrich search results with fuller details for movies/tv when possible
            try:
                if content_type == 'movie':
                    details = fetch_tmdb_movie(tmdb_id) or {}
                    # fetch_tmdb_movie returns keys like 'runtime', 'imdb_id', 'genres', etc.
                    base_result.update({
                        'runtime': details.get('runtime'),
                        'imdb_id': details.get('imdb_id'),
                        'genres': details.get('genres', []),
                        'director': details.get('director'),
                        'description': details.get('description') or base_result.get('description', ''),
                        'poster_url': details.get('poster_url') or base_result.get('poster_url', ''),
                    })
                else:
                    details = fetch_tmdb_tv(tmdb_id) or {}
                    base_result.update({
                        'total_seasons': details.get('total_seasons'),
                        'total_episodes': details.get('total_episodes'),
                        'episodes_per_season': details.get('episodes_per_season', {}),
                        'description': details.get('description') or base_result.get('description', ''),
                        'poster_url': details.get('poster_url') or base_result.get('poster_url', ''),
                    })
            except Exception:
                # If enrichment fails, keep the lightweight result
                pass

            results.append(base_result)

        # Cache search results briefly to reduce load
        cache.set(cache_key, results, 60)
        return results
    except Exception as e:
        print(f"Error searching TMDB: {e}")
        return []


def get_recommendations_based_on_ratings(user_ratings: List[Rating] = None) -> List[Dict]:
    """
    Generate recommendations based on user's ratings
    Simple implementation: recommends based on genre preferences
    """
    # Try cached recommendations first (short TTL)
    cache_key = 'recommendations_v2'
    cached_recs = cache.get(cache_key)
    if cached_recs:
        return cached_recs

    # If caller provided ratings, use them; otherwise fetch all ratings
    ratings_qs = user_ratings if user_ratings is not None else Rating.objects.all()

    # Build a set of content ids the user has interacted with so we can exclude them
    interacted_ids = set()
    # From ratings
    try:
        interacted_ids.update(list(ratings_qs.values_list('content_id', flat=True)))
    except Exception:
        # If ratings_qs is not a queryset (e.g., list), handle accordingly
        try:
            interacted_ids.update([r.content_id for r in ratings_qs])
        except Exception:
            pass

    # From watch progress (completed episodes)
    completed_progress = WatchProgress.objects.filter(completed=True).values_list('content_id', flat=True)
    interacted_ids.update(list(completed_progress))

    # From watch history (user actually watched something)
    watched_history = WatchHistory.objects.all().values_list('content_id', flat=True)
    interacted_ids.update(list(watched_history))

    # Calculate genre preference scores using weighted ratings and watch signals
    genre_scores = {}

    # Weight ratings: rating 6->1, 7->2, ... 10->5 (rating-5)
    for rating in ratings_qs:
        weight = max(0, rating.rating - 5)
        if weight <= 0:
            continue
        for genre in rating.content.genre.all():
            genre_scores[genre.name] = genre_scores.get(genre.name, 0) + weight

    # Weight watch history: give a small boost for watched contents
    for content_id in set(list(watched_history)):
        try:
            content = Content.objects.get(id=content_id)
            for genre in content.genre.all():
                genre_scores[genre.name] = genre_scores.get(genre.name, 0) + 1
        except Content.DoesNotExist:
            continue

    # Also consider Content with status 'completed' as a strong signal
    completed_contents = Content.objects.filter(status='completed')
    for c in completed_contents:
        for genre in c.genre.all():
            genre_scores[genre.name] = genre_scores.get(genre.name, 0) + 2
        interacted_ids.add(c.id)

    # If no strong signals, fall back to top-rated global content
    if not genre_scores:
        # Top rated content excluding already interacted
        from django.db.models import Avg
        rated = Content.objects.annotate(avg_rating=Avg('ratings__rating')).exclude(id__in=interacted_ids).order_by('-avg_rating')[:10]
        recs = [
            {
                'id': content.id,
                'title': content.title,
                'content_type': content.content_type,
                'poster_url': content.poster_url,
                'genre': [g.name for g in content.genre.all()],
            }
            for content in rated
        ]
        cache.set(cache_key, recs, 60 * 5)
        return recs

    # Pick top genres
    top_genres = [g for g, _ in sorted(genre_scores.items(), key=lambda x: x[1], reverse=True)[:3]]

    # Find content in those genres not already interacted with
    recommendations = Content.objects.filter(genre__name__in=top_genres).exclude(id__in=interacted_ids).distinct()

    # Order recommendations by average rating (fallback to created_at)
    from django.db.models import Avg
    recommendations = recommendations.annotate(avg_rating=Avg('ratings__rating')).order_by('-avg_rating', '-created_at')[:20]

    rec_list = [
        {
            'id': content.id,
            'title': content.title,
            'content_type': content.content_type,
            'poster_url': content.poster_url,
            'genre': [g.name for g in content.genre.all()],
        }
        for content in recommendations
    ]

    if not rec_list:
        # Try TMDB-based recommendations (returns tmdb_id, title, description, poster_url)
        tmdb_results = recommend_from_tmdb_genres(top_genres, limit=20)
        if tmdb_results:
            cache.set(cache_key, tmdb_results, 60 * 5)
            return tmdb_results

    cache.set(cache_key, rec_list, 60 * 5)
    return rec_list
    

def _fetch_tmdb_genre_map(api_key: str) -> Dict[str, int]:
    """Return a mapping of TMDB genre name -> genre id for movies."""
    cache_key = f"tmdb_genre_map"
    cached = cache.get(cache_key)
    if cached:
        return cached

    try:
        resp = requests.get('https://api.themoviedb.org/3/genre/movie/list', params={'api_key': api_key, 'language': 'en-US'}, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        mapping = {g['name'].lower(): g['id'] for g in data.get('genres', [])}
        cache.set(cache_key, mapping, 60 * 60 * 24)
        return mapping
    except Exception:
        return {}


def recommend_from_tmdb_genres(top_genres: List[str], limit: int = 20) -> List[Dict]:
    """Use TMDB discover to find popular movies and TV shows for given genre names.

    Returns a mixed list of movies and TV shows (tmdb_id, title, description, poster_url, release_date).
    """
    api_key = settings.TMDB_API_KEY
    if not api_key or not top_genres:
        return []

    genre_map = _fetch_tmdb_genre_map(api_key)
    genre_ids = []
    for name in top_genres:
        gid = genre_map.get(name.lower())
        if gid:
            genre_ids.append(str(gid))

    if not genre_ids:
        return []

    existing_tmdb_ids = set(Content.objects.filter(tmdb_id__isnull=False).values_list('tmdb_id', flat=True))
    results = []

    def _collect_from(endpoint: str, params: Dict):
        try:
            resp = requests.get(endpoint, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            for item in data.get('results', [])[:limit * 2]:
                tmdb_id = item.get('id')
                if tmdb_id in existing_tmdb_ids:
                    continue
                poster = item.get('poster_path')
                results.append({
                    'tmdb_id': tmdb_id,
                    'title': item.get('title') or item.get('name'),
                    'description': item.get('overview') or '',
                    'release_date': item.get('release_date') or item.get('first_air_date'),
                    'poster_url': f"https://image.tmdb.org/t/p/w500{poster}" if poster else '',
                })
                if len(results) >= limit:
                    return
        except Exception:
            return

    base_params = {
        'api_key': api_key,
        'language': 'en-US',
        'with_genres': ','.join(genre_ids),
        'sort_by': 'popularity.desc',
        'page': 1,
    }

    # collect movies
    _collect_from('https://api.themoviedb.org/3/discover/movie', base_params)
    # collect tv shows as well
    _collect_from('https://api.themoviedb.org/3/discover/tv', base_params)

    return results[:limit]


def estimate_completion_time(content: Content, avg_watch_time_per_day: int = 120) -> Dict:
    """
    Estimate time to complete a show based on watching habits
    avg_watch_time_per_day in minutes
    """
    if content.content_type != 'tv_show':
        return {'estimated_days': None, 'message': 'Only available for TV shows'}
    
    tv_show = TVShow.objects.get(id=content.id)
    total_episodes = tv_show.total_episodes
    
    # Calculate watched episodes
    watched = content.watch_progress.filter(completed=True).count()
    remaining = total_episodes - watched
    
    if remaining <= 0:
        return {'estimated_days': 0, 'message': 'Show already completed'}
    
    # Assume average episode runtime if not available
    avg_episode_time = content.runtime or 45  # Default 45 minutes per episode
    
    total_minutes_needed = remaining * avg_episode_time
    estimated_days = total_minutes_needed / avg_watch_time_per_day
    
    return {
        'estimated_days': round(estimated_days, 1),
        'remaining_episodes': remaining,
        'total_episodes': total_episodes,
        'watched_episodes': watched,
        'completion_percentage': round((watched / total_episodes) * 100, 1) if total_episodes > 0 else 0,
    }


def generate_review_from_notes(notes: str) -> str:
    """
    Generate a review from user notes
    Simple implementation - can be enhanced with AI/LLM
    """
    if not notes:
        return ""
    
    # Simple template-based generation
    # In production, this could use OpenAI API or similar
    review_parts = []
    
    if len(notes) > 50:
        review_parts.append(notes[:200] + "...")
    else:
        review_parts.append(notes)
    
    return " ".join(review_parts)


def _safe_parse_date(date_str: str) -> Optional[str]:
    """Convert OMDB style date (e.g. 01 Jan 2020) into ISO string"""
    if not date_str or date_str == 'N/A':
        return None
    for fmt in ("%d %b %Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(date_str, fmt).date().isoformat()
        except ValueError:
            continue
    return None


def _safe_parse_runtime(runtime_str: str) -> Optional[int]:
    if not runtime_str or runtime_str == 'N/A':
        return None
    parts = runtime_str.split()
    for part in parts:
        if part.isdigit():
            return int(part)
    return None


def search_omdb(query: str, content_type: str = 'movie') -> List[Dict]:
    """Search OMDB API for movies/series"""
    api_key = settings.OMDB_API_KEY
    if not api_key:
        return []

    omdb_type = 'movie' if content_type == 'movie' else 'series'
    params = {
        'apikey': api_key,
        's': query,
        'type': omdb_type,
    }

    try:
        response = requests.get("https://www.omdbapi.com/", params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get('Response') != 'True':
            return []

        results = []
        for item in data.get('Search', []):
            poster = item.get('Poster')
            results.append({
                'imdb_id': item.get('imdbID'),
                'title': item.get('Title'),
                'description': '',
                'release_date': item.get('Year'),
                'poster_url': '' if poster in (None, 'N/A') else poster,
            })
        return results
    except Exception as exc:
        print(f"Error searching OMDB: {exc}")
        return []


def fetch_omdb_title(imdb_id: str) -> Optional[Dict]:
    """Fetch detailed information from OMDB using imdb id"""
    api_key = settings.OMDB_API_KEY
    if not api_key or not imdb_id:
        return None

    params = {
        'apikey': api_key,
        'i': imdb_id,
        'plot': 'full',
    }

    try:
        response = requests.get("https://www.omdbapi.com/", params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get('Response') != 'True':
            return None

        genres = [genre.strip() for genre in data.get('Genre', '').split(',') if genre.strip() and genre.strip() != 'N/A']
        release_date = _safe_parse_date(data.get('Released'))
        runtime = _safe_parse_runtime(data.get('Runtime'))
        content_type = 'movie' if data.get('Type') == 'movie' else 'tv_show'
        total_seasons = data.get('totalSeasons')

        return {
            'title': data.get('Title'),
            'description': data.get('Plot') if data.get('Plot') != 'N/A' else '',
            'release_date': release_date,
            'poster_url': '' if data.get('Poster') in (None, 'N/A') else data.get('Poster'),
            'runtime': runtime,
            'imdb_id': data.get('imdbID'),
            'genres': genres,
            'director': data.get('Director') if data.get('Director') != 'N/A' else '',
            'content_type': content_type,
            'total_seasons': int(total_seasons) if total_seasons and total_seasons.isdigit() else 1,
            'total_episodes': 0,
        }
    except Exception as exc:
        print(f"Error fetching OMDB title: {exc}")
        return None


