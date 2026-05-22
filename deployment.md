# Deployment Guide - RateMyShow

Complete guide to deploy RateMyShow to Render.com with Supabase PostgreSQL.

## 📋 Prerequisites

1. **Render Account**: https://render.com (free tier available)
2. **Supabase Account**: https://supabase.com (free PostgreSQL database)
3. **GitHub Account**: For deploying from git repository
4. **OMDB API Key**: Get free at http://www.omdbapi.com
5. **Email Service**: Gmail or SendGrid for password resets

## 🗄️ Step 1: Set Up Supabase PostgreSQL

### Create Supabase Project

1. Go to https://supabase.com
2. Click "New Project"
3. Choose a name (e.g., "ratemyshow")
4. Set a strong password
5. Choose region closest to users
6. Wait for database creation (2-3 minutes)

### Get Connection String

1. In Supabase dashboard, go to "Settings" → "Database"
2. Copy **Connection string** (URI format)
3. It looks like: `postgresql://postgres:[PASSWORD]@db.[PROJECT].supabase.co:5432/postgres`
4. Save it as your `DATABASE_URL`

### Enable UUID Extension (Optional)

In Supabase SQL Editor:
```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

## 🚀 Step 2: Deploy to Render.com

### Option A: Using render.yaml (Recommended)

1. **Fork/Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/ratemyshow.git
   git push -u origin main
   ```

2. **Go to Render Dashboard**
   - https://dashboard.render.com

3. **Create New → Blueprint**
   - Select your GitHub repository
   - Render will use `render.yaml`
   - Configure environment variables (see below)

4. **Environment Variables**
   - `DEBUG`: `false`
   - `DJANGO_SECRET_KEY`: Generate random string
   - `DATABASE_URL`: From Supabase (with postgresql://)
   - `OMDB_API_KEY`: Your OMDB key
   - `EMAIL_HOST_USER`: Your Gmail/SendGrid
   - `EMAIL_HOST_PASSWORD`: App password
   - `ALLOWED_HOSTS`: Your render domain

5. **Deploy**
   - Click "Deploy"
   - Wait 5-10 minutes for completion
   - Visit your live app!

### Option B: Manual Deployment

1. **Create Web Service**
   - Name: `ratemyshow`
   - Runtime: Python 3.10
   - Build command: `pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput`
   - Start command: `gunicorn rateMySh.wsgi:application`

2. **Create PostgreSQL Database**
   - Use Supabase instead (recommended)
   - Or use Render's PostgreSQL (paid)

3. **Create Redis Cache**
   - Name: `ratemyshow-redis`
   - Plan: Free

4. **Set Environment Variables**
   - See table below

5. **Add Custom Domain (Optional)**
   - In Render settings → Custom Domain
   - Point your domain DNS

## 🔐 Environment Variables

| Variable | Value | Notes |
|----------|-------|-------|
| `DEBUG` | `false` | Never True in production |
| `DJANGO_SECRET_KEY` | Random 50+ chars | Generate: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` |
| `DATABASE_URL` | `postgresql://...` | From Supabase |
| `ALLOWED_HOSTS` | `yourdomain.com,*.onrender.com` | Your Render subdomain |
| `OMDB_API_KEY` | Your API key | Get free at omdbapi.com |
| `EMAIL_BACKEND` | `django.core.mail.backends.smtp.EmailBackend` | For Gmail: keep as-is |
| `EMAIL_HOST` | `smtp.gmail.com` | Gmail SMTP server |
| `EMAIL_PORT` | `587` | Gmail TLS port |
| `EMAIL_USE_TLS` | `true` | Enable TLS for Gmail |
| `EMAIL_HOST_USER` | `your-email@gmail.com` | Your Gmail address |
| `EMAIL_HOST_PASSWORD` | `app-password` | Gmail app password (not regular password) |
| `SECURE_SSL_REDIRECT` | `true` | Always use HTTPS |
| `SESSION_COOKIE_SECURE` | `true` | Only send cookie over HTTPS |
| `CSRF_COOKIE_SECURE` | `true` | CSRF protection |
| `REDIS_URL` | `redis://...` | From Render Redis or external |

## 📧 Setting Up Gmail for Email Verification

### Generate Gmail App Password

1. Go to https://myaccount.google.com/apppasswords
2. Select "Mail" and "Windows Computer" (or your device)
3. Google generates a 16-character password
4. Copy this as your `EMAIL_HOST_PASSWORD`
5. **NOT your regular Gmail password!**

### Alternative: SendGrid

1. Create SendGrid account (free tier: 100/day)
2. Get API key
3. Use settings:
   ```
   EMAIL_BACKEND=sendgrid_backend.SendgridBackend
   SENDGRID_API_KEY=your_api_key
   ```

## ✅ Post-Deployment Checklist

After deployment, run these commands:

### 1. SSH into Render Instance
```bash
# Via Render Dashboard → Shell tab
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

### 2. Verify Settings
- Visit `/admin` and login
- Check database connection
- Verify static files load

### 3. Test Features
- [ ] User registration works
- [ ] Email verification sends
- [ ] Search finds movies
- [ ] Rating system works
- [ ] Watchlist persists
- [ ] Recommendations generate

### 4. Monitor Logs
```bash
# In Render Dashboard
# Check "Logs" tab for errors
tail -f build.log  # Build errors
tail -f deploy.log # Deployment logs
```

## 🔄 Updates & Maintenance

### Deploying Updates

```bash
# Make changes locally
git add .
git commit -m "Your message"
git push origin main

# Render auto-deploys on push (if configured)
# Or manually redeploy from Render dashboard
```

### Running Management Commands

Via Render Shell:
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py shell
```

### Database Backups

Supabase includes backups. Manual export:
```bash
# Via Supabase Dashboard → Backups
# Or via CLI:
pg_dump $DATABASE_URL > backup.sql
```

## 🔧 Troubleshooting

### "502 Bad Gateway"
- Check application logs
- Verify `ALLOWED_HOSTS` includes your domain
- Ensure migrations ran successfully

### "Disallowed host"
- Add your domain to `ALLOWED_HOSTS` env var
- Include `.onrender.com` subdomain

### "Static files 404"
- Run `python manage.py collectstatic --noinput`
- Check `STATIC_ROOT` and `STATIC_URL`
- Ensure WhiteNoise middleware is active

### "Database connection refused"
- Verify `DATABASE_URL` format
- Check Supabase credentials
- Ensure IP allowlisting (if needed)
- Test: `psql $DATABASE_URL -c "SELECT 1"`

### "Email not sending"
- Verify `EMAIL_HOST_PASSWORD` is app password, not regular password
- Check `EMAIL_HOST_USER` matches
- Review Django logs for SMTP errors
- Try sending from admin: `/admin` → Users → Change

### "Slow recommendations"
- Recommendations run on first access and cache
- Pre-compute: Run management command daily
- Increase Redis memory if available

## 📊 Monitoring

### Render Dashboard
- Check logs regularly
- Monitor CPU/Memory usage
- Set up alerts for errors

### Error Tracking (Optional)
Add Sentry for error monitoring:
```python
# In settings.py
import sentry_sdk
sentry_sdk.init("your_sentry_dsn", ...)
```

## 💰 Cost Estimation

| Service | Free Tier | Paid |
|---------|-----------|------|
| Render Web | 750 hours/month | $7/month+ |
| Render Redis | None (Paid $6/month) | $6/month+ |
| Supabase | 500MB storage, unlimited API | $25/month+ |
| **Total** | ~$6/month | $15+/month |

## 🔒 Security Checklist

- [ ] `DEBUG=false` in production
- [ ] `DJANGO_SECRET_KEY` is random, 50+ chars
- [ ] `ALLOWED_HOSTS` configured correctly
- [ ] `SECURE_SSL_REDIRECT=true`
- [ ] All cookies are secure (HTTPS only)
- [ ] Database password is strong
- [ ] Email credentials not in code
- [ ] Git ignored `.env` file
- [ ] No secrets in git history
- [ ] CORS properly configured

## 📞 Support Resources

- **Render Docs**: https://render.com/docs
- **Supabase Docs**: https://supabase.com/docs
- **Django Docs**: https://docs.djangoproject.com
- **Tailwind CSS**: https://tailwindcss.com/docs

## Next Steps

1. ✅ Deploy to Render
2. ✅ Configure domain (optional)
3. ✅ Set up monitoring
4. ✅ Test all features
5. ✅ Start rating movies!

---

**Questions?** Check render.yaml configuration or Django deployment best practices.
