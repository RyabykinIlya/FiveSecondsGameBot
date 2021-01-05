from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt

from telegram import Update, Bot
import json

from bot.settings import TOKEN
from bot.dispatcher import dispatcher


@csrf_exempt
def webhook_in(request, token):
    if not token == TOKEN:
        return HttpResponseForbidden("Page forbidden.")
    json_data = json.loads(request.body)
    update = Update.de_json(json_data, Bot(token=token))
    dispatcher.process_update(update)
    return HttpResponse("")
