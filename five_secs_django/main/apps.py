from django.apps import AppConfig
from django.conf import settings

from time import sleep
import os


class MainConfig(AppConfig):
    name = 'five_secs_django.main'

    def ready(self):
        from bot.settings import TOKEN
        from bot.dispatcher import updater
        HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")
        if not settings.DEBUG:
            HEROKU_APP_NAME += '.herokuapp.com'
        # django run this code twice using gunicorn through heroku
        sleep(2)
        updater.bot.setWebhook('https://%s/%s' % (HEROKU_APP_NAME, TOKEN))
