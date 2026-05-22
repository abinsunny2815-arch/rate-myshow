"""
Quick start and feature documentation.
"""

# QUICK START GUIDE

## Local Development
```bash
# 1. Setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# 2. Configure .env with:
# - DATABASE_URL (Supabase)
# - DJANGO_SECRET_KEY
# - OMDB_API_KEY=d5b0159b

# 3. Run
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Features Quick Links
- Home: http://localhost:8000/
- Admin: http://localhost:8000/admin/
- Search: http://localhost:8000/search/
- Top Movies: http://localhost:8000/top-movies/
- Recommendations: http://localhost:8000/recommendations/

## API Examples
```
# Search
GET /api/titles/search/?q=Inception

# Title Detail
GET /api/titles/tt1375666/
```

## Database Models Overview
- **CustomUser**: Extended Django user with profile
- **Title**: Movie/TV show with OMDB data
- **Rating**: 1-10 user rating for title
- **Review**: Text review with spoiler flag
- **Watchlist**: Personal to-watch list
- **Recommendation**: Personalized suggestions
- **Genre, Actor, Person**: Relations
- **UserActivity**: Track user actions

## Recommendation System
- Content-based: Similar genres/actors
- Collaborative: Similar user ratings
- Hybrid scoring with confidence

## Settings Key Variables
```python
# In rateMySh/settings.py
OMDB_API_KEY = 'd5b0159b'
OMDB_CACHE_TIMEOUT = 86400 * 30  # 30 days
MIN_COMMON_RATINGS = 2
SIMILARITY_THRESHOLD = 0.3
ITEMS_PER_PAGE = 20
```

## Common Tasks

### Load Initial Data
```bash
python manage.py load_initial_data --movies 50 --shows 50
```

### Update Recommendations for User
```bash
python manage.py shell
>>> from apps.recommendations.services import RecommendationEngine
>>> from apps.users.models import CustomUser
>>> user = CustomUser.objects.first()
>>> engine = RecommendationEngine()
>>> engine.update_recommendations_for_user(user)
```

### Test OMDB API
```bash
python manage.py shell
>>> from apps.core.services import OMDBService
>>> service = OMDBService()
>>> data = service.get_title('tt1375666')  # Inception
>>> print(data['Title'])
```

## Static Files
```bash
# Development: Automatic via Django
# Production: Run collectstatic
python manage.py collectstatic --noinput
```

## Deployment Checklist
- [ ] Set DEBUG=False
- [ ] Generate new SECRET_KEY
- [ ] Configure DATABASE_URL
- [ ] Set ALLOWED_HOSTS
- [ ] Configure email backend
- [ ] Run migrations
- [ ] Collect static files
- [ ] Create superuser
- [ ] Test features
- [ ] Monitor logs

## Support
- Django Docs: https://docs.djangoproject.com
- OMDB API: http://www.omdbapi.com
- Tailwind CSS: https://tailwindcss.com
- PostgreSQL: https://www.postgresql.org/docs/
