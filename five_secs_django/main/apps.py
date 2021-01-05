from django.apps import AppConfig
from django.conf import settings

from telegram.error import RetryAfter
import os


class MainConfig(AppConfig):
    name = 'five_secs_django.main'

    def ready(self):
        from bot.settings import TOKEN
        from bot.dispatcher import updater
        HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")
        if not settings.DEBUG:
            HEROKU_APP_NAME += '.herokuapp.com'
        try:
            updater.bot.setWebhook('https://%s/%s' % (HEROKU_APP_NAME, TOKEN))
        except RetryAfter:
            pass
