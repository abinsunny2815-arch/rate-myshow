release: python manage.py migrate
web: gunicorn rateMySh.wsgi:application
worker: celery -A rateMySh worker -l info
