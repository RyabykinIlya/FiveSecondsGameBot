release: python manage.py migrate
web: gunicorn five_secs_django.wsgi
worker: python3 bot/start.py
