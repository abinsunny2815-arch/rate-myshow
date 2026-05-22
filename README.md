# RateMyShow - Movie & TV Show Rating Platform

A production-ready Django web application for rating and reviewing movies and TV shows, similar to IMDb. Built with Django 5.x, PostgreSQL (Supabase), and modern frontend technologies.

## 🎬 Features

### Core Features
- **User Authentication**: Registration, login, password reset, email verification
- **Movie & TV Show Database**: Powered by OMDB API with caching
- **Rating System**: 1-10 star ratings with 0.5 increments
- **Reviews**: Write detailed reviews with spoiler tags
- **Watchlist**: Personal to-watch, watching, completed, and dropped lists
- **Personalized Recommendations**: Hybrid recommendation system (content-based + collaborative filtering)

### Advanced Features
- **Top 250 Rankings**: Movies and TV shows ranked by community ratings
- **Genre Browsing**: Filter and explore by genre
- **Activity Feed**: See what others are rating and reviewing
- **User Profiles**: Public profiles showing ratings, reviews, and watchlist
- **Search**: Global AJAX search for titles
- **Dark Mode**: Beautiful dark theme optimized for viewing
- **Responsive Design**: Mobile-first, works perfectly on all devices

## 🚀 Tech Stack

- **Backend**: Python 3.10+, Django 5.x
- **Database**: PostgreSQL (Supabase)
- **Frontend**: HTML5, Tailwind CSS, Alpine.js, Vanilla JavaScript
- **API**: OMDB API for title data, Django REST Framework
- **Caching**: Redis
- **Async Tasks**: Celery
- **Deployment**: Render.com
- **Static Files**: WhiteNoise

## 📋 Project Structure

```
rate myshow/
├── rateMySh/                 # Project configuration
│   ├── settings.py           # Django settings (Supabase, caching, etc.)
│   ├── urls.py               # URL routing
│   ├── wsgi.py               # WSGI configuration
│   ├── asgi.py               # ASGI configuration
│   └── celery.py             # Celery configuration
├── apps/
│   ├── core/                 # Core app (home, search, activity feed)
│   ├── titles/               # Movies & TV shows management
│   ├── users/                # User authentication & profiles
│   ├── ratings/              # Ratings & reviews
│   └── recommendations/      # Recommendation engine
├── templates/                # HTML templates
│   ├── layouts/              # Base template
│   ├── core/                 # Home, search, etc.
│   ├── auth/                 # Login, register
│   ├── titles/               # Title detail page
│   ├── users/                # Profile, watchlist
│   ├── ratings/              # Review form
│   └── errors/               # 404, 500 errors
├── static/
│   ├── css/                  # Custom Tailwind CSS
│   └── js/                   # JavaScript utilities
├── media/                    # User uploads (avatars, etc.)
├── requirements.txt          # Python dependencies
├── manage.py                 # Django management script
├── Procfile                  # Render deployment configuration
├── render.yaml               # Render blueprint
├── .env.example              # Environment variables template
└── README.md                 # This file
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.10+
- PostgreSQL database (Supabase account recommended)
- Redis instance
- OMDB API key (free at http://www.omdbapi.com)

### Local Development

1. **Clone the repository**
   ```bash
   cd "rate myshow"
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings:
   # - DATABASE_URL (Supabase PostgreSQL)
   # - DJANGO_SECRET_KEY (generate with: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
   # - OMDB_API_KEY
   # - Email configuration (Gmail, SendGrid, etc.)
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Collect static files**
   ```bash
   python manage.py collectstatic --noinput
   ```

8. **Run development server**
   ```bash
   python manage.py runserver
   ```

   Visit `http://localhost:8000`

## 🗄️ Database Models

### CustomUser
- Extended Django user with profile info
- Avatar, bio, theme preference
- Privacy controls, rating/review counts

### Title
- Movie or TV show data from OMDB
- Genres, cast, crew, plot, ratings
- Average rating and count (cached)

### Rating
- User rating (1-10) for a title
- Unique per user per title

### Review
- User review with spoiler flag
- Linked to rating (optional)
- Helpful/unhelpful count for UX

### Watchlist
- Personal watchlist entry
- Status: to-watch, watching, completed, dropped
- Priority and notes

### Recommendation
- Personalized recommendations
- Confidence score and reason
- Dismissible

## 🤖 Recommendation Engine

The recommendation system uses a hybrid approach:

1. **Content-Based Filtering**
   - Analyzes genres and actors user rated highly
   - Recommends similar content
   - Fast, no cold-start problem

2. **Collaborative Filtering**
   - Finds users with similar rating patterns
   - Uses cosine similarity on rating vectors
   - Recommends what similar users rated highly

3. **Hybrid Scoring**
   - Combines both approaches with confidence scores
   - Prioritizes collaborative results
   - Updates daily/on-demand

## 🔑 API Endpoints

All endpoints return JSON. See `apps/titles/api_views.py`:

- `GET /api/titles/search/?q=<query>` - Search titles
- `GET /api/titles/<omdb_id>/` - Get title details

## ⚙️ Configuration

### Environment Variables

See `.env.example` for all options:

```
DEBUG=False
DJANGO_SECRET_KEY=<generate-random>
DATABASE_URL=postgresql://user:pass@host:5432/dbname
OMDB_API_KEY=<your-api-key>
EMAIL_HOST_USER=<your-email>
EMAIL_HOST_PASSWORD=<app-password>
REDIS_URL=redis://localhost:6379/0
```

### Important Settings

- **OMDB_CACHE_TIMEOUT**: 30 days (86400 * 30 seconds)
- **MIN_COMMON_RATINGS**: 2 (for collaborative filtering)
- **SIMILARITY_THRESHOLD**: 0.3 (cosine similarity)
- **ITEMS_PER_PAGE**: 20 (pagination)

## 🚀 Deployment

See [deployment.md](deployment.md) for detailed Render.com deployment instructions.

Quick start:
1. Create Render account and connect GitHub
2. Use `render.yaml` blueprint
3. Set environment variables
4. Deploy!

## 📚 Development

### Creating superuser
```bash
python manage.py createsuperuser
```

### Admin panel
Access at `/admin` with superuser credentials

### Running tests
```bash
pytest
```

### Creating migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Clearing cache
```bash
python manage.py shell
>>> from django.core.cache import cache
>>> cache.clear()
```

## 🐛 Common Issues

### "OMDB API key not working"
- Check `.env` has correct key
- Test at http://www.omdbapi.com/?apikey=YOUR_KEY&t=Inception

### "Database connection refused"
- Verify `DATABASE_URL` in `.env`
- Check Supabase credentials
- Run `python manage.py dbshell` to test

### "Static files not showing in production"
- Run `python manage.py collectstatic --noinput`
- Check `STATIC_ROOT` and `STATIC_URL` in settings

### "Recommendations not updating"
- Ensure Redis is running
- Check Celery logs: `celery -A rateMySh worker -l info`
- Manual update: `python manage.py shell` → `RecommendationEngine().update_recommendations_for_user(user)`

## 📝 License

MIT License - Feel free to use for personal or commercial projects.

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Performance optimization
- Additional recommendation algorithms
- UI/UX enhancements
- Integration with other APIs (Trailer.com, IMDb charts)
- Advanced search filters
- Social features (follow users, like reviews)

## 📞 Support

- Check GitHub Issues for known problems
- Review Django/DRF documentation
- OMDB API docs: http://www.omdbapi.com
- Tailwind CSS: https://tailwindcss.com

## 🎯 Future Roadmap

- [ ] Trailer integration
- [ ] User following/social features
- [ ] Advanced search with filters
- [ ] Email notifications
- [ ] Mobile app
- [ ] GraphQL API
- [ ] User-generated collections/lists
- [ ] Rating by mood/genre
- [ ] Integration with Netflix, IMDB data

---

**Built with ❤️ using Django**
