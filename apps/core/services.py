"""
OMDB API integration service.
"""
import requests
import logging
from django.conf import settings
from django.core.cache import cache
from apps.titles.models import Title, Genre, Actor
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)


class OMDBService:
    """Service for interacting with OMDB API."""
    
    BASE_URL = 'http://www.omdbapi.com/'
    
    def __init__(self, api_key: str = None, timeout: int = None):
        self.api_key = api_key or settings.OMDB_API_KEY
        self.timeout = timeout or settings.OMDB_API_TIMEOUT
    
    def _make_request(self, params: Dict) -> Optional[Dict]:
        """Make HTTP request to OMDB API."""
        try:
            params['apikey'] = self.api_key
            response = requests.get(self.BASE_URL, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            if data.get('Response') == 'False':
                logger.warning(f"OMDB Error: {data.get('Error')}")
                return None
            
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"OMDB API request failed: {e}")
            return None
    
    def search(self, query: str, type_: str = None, year: int = None, page: int = 1) -> Optional[Dict]:
        """Search for titles."""
        params = {
            's': query,
            'page': page,
            'type': type_,
        }
        if year:
            params['y'] = year
        
        cache_key = f"omdb_search:{query}:{type_}:{year}:{page}"
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        data = self._make_request(params)
        if data:
            cache.set(cache_key, data, settings.OMDB_CACHE_TIMEOUT)
        
        return data
    
    def get_title(self, omdb_id: str) -> Optional[Dict]:
        """Get full title data by OMDB ID."""
        params = {'i': omdb_id, 'plot': 'full', 'type': 'movie'}
        
        cache_key = f"omdb_title:{omdb_id}"
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        data = self._make_request(params)
        if data:
            cache.set(cache_key, data, settings.OMDB_CACHE_TIMEOUT)
        
        return data
    
    def sync_title_to_db(self, omdb_id: str) -> Optional[Title]:
        """Fetch title from OMDB and save/update in database."""
        omdb_data = self.get_title(omdb_id)
        if not omdb_data:
            return None
        
        title_obj, created = Title.objects.update_or_create(
            omdb_id=omdb_id,
            defaults={
                'title': omdb_data.get('Title'),
                'type': omdb_data.get('Type', 'movie').lower(),
                'year': self._parse_year(omdb_data.get('Year')),
                'released_date': self._parse_date(omdb_data.get('Released')),
                'rated': omdb_data.get('Rated', ''),
                'runtime': self._parse_runtime(omdb_data.get('Runtime')),
                'plot': omdb_data.get('Plot', ''),
                'poster_url': omdb_data.get('Poster', ''),
                'imdb_rating': self._parse_float(omdb_data.get('imdbRating')),
                'imdb_votes': self._parse_int(omdb_data.get('imdbVotes')),
                'director': omdb_data.get('Director', ''),
                'writer': omdb_data.get('Writer', ''),
                'production': omdb_data.get('Production', ''),
                'country': omdb_data.get('Country', ''),
                'language': omdb_data.get('Language', ''),
                'omdb_data': omdb_data,
            }
        )
        
        # Add genres
        if 'Genre' in omdb_data:
            genres = [g.strip() for g in omdb_data['Genre'].split(',')]
            for genre_name in genres:
                genre_obj, _ = Genre.objects.get_or_create(
                    name=genre_name,
                    defaults={'slug': self._slugify(genre_name)}
                )
                title_obj.genres.add(genre_obj)
        
        # Add actors
        if 'Actors' in omdb_data:
            actors = [a.strip() for a in omdb_data['Actors'].split(',')]
            for actor_name in actors:
                actor_obj, _ = Actor.objects.get_or_create(name=actor_name)
                title_obj.actors.add(actor_obj)
        
        return title_obj
    
    @staticmethod
    def _parse_year(year_str: str) -> Optional[int]:
        """Parse year from OMDB year string."""
        if not year_str:
            return None
        try:
            # Handle ranges like "1990–1991"
            year = year_str.split('–')[0].split('-')[0]
            return int(year)
        except (ValueError, IndexError):
            return None
    
    @staticmethod
    def _parse_runtime(runtime_str: str) -> Optional[int]:
        """Parse runtime minutes from OMDB runtime string."""
        if not runtime_str:
            return None
        try:
            return int(runtime_str.split()[0])
        except (ValueError, IndexError):
            return None
    
    @staticmethod
    def _parse_int(value_str: str) -> int:
        """Parse integer from string."""
        if not value_str:
            return 0
        try:
            return int(value_str.replace(',', ''))
        except ValueError:
            return 0
    
    @staticmethod
    def _parse_float(value_str: str) -> Optional[float]:
        """Parse float from string."""
        if not value_str or value_str == 'N/A':
            return None
        try:
            return float(value_str)
        except ValueError:
            return None
    
    @staticmethod
    def _parse_date(date_str: str) -> Optional[str]:
        """Parse date from OMDB format (e.g., '14 Oct 1994') to YYYY-MM-DD."""
        if not date_str or date_str == 'N/A':
            return None
        try:
            from datetime import datetime
            parsed = datetime.strptime(date_str, '%d %b %Y')
            return parsed.strftime('%Y-%m-%d')
        except ValueError:
            return None
    
    @staticmethod
    def _slugify(text: str) -> str:
        """Simple slug generation."""
        return text.lower().replace(' ', '-').replace('&', 'and')


class TrendingService:
    """Service for managing trending titles."""
    
    @staticmethod
    def get_trending_this_week() -> List[Title]:
        """Get trending titles for this week."""
        cache_key = 'trending_this_week'
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        from django.utils import timezone
        from datetime import timedelta
        
        week_ago = timezone.now() - timedelta(days=7)
        trending = Title.objects.filter(
            ratings__created_at__gte=week_ago
        ).annotate(
            ratings_count=models.Count('ratings')
        ).order_by('-ratings_count')[:50]
        
        cache.set(cache_key, list(trending), 3600)  # Cache for 1 hour
        return trending
    
    @staticmethod
    def get_popular_movies() -> List[Title]:
        """Get popular movies."""
        cache_key = 'popular_movies'
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        popular = Title.objects.filter(
            type='movie',
            rating_count__gt=10
        ).order_by('-avg_rating', '-rating_count')[:50]
        
        cache.set(cache_key, list(popular), 3600)
        return popular
    
    @staticmethod
    def get_top_tv_shows() -> List[Title]:
        """Get top-rated TV shows."""
        cache_key = 'top_tv_shows'
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        top = Title.objects.filter(
            type='series',
            rating_count__gt=5
        ).order_by('-avg_rating', '-rating_count')[:50]
        
        cache.set(cache_key, list(top), 3600)
        return top


from django.db import models
