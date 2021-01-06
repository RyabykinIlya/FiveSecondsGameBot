from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
import re
import importlib

# export PYTHONPATH=/home/iryabykin/DATA/shared/Development/five_seconds_bot
# python bot/dispatcher.py

# import django
# import os

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "five_secs_django.settings")
# django.setup()

from bot.handlers import button
from bot.utils import get_chat, initialize_state_if_not, remove_last_markup
from bot import settings

updater = Updater(token=settings.TOKEN, use_context=True)
dispatcher = updater.dispatcher


def handlers_dispatcher(update: Update, context: CallbackContext) -> None:
    """
    function to define basic models and invoke right handler
    """
    handler_name = update.message["text"]

    try:
        handler_name = re.search('\/([a-z_]+)', handler_name).group(1)
    except AttributeError:
        return

    module = importlib.import_module("bot.handlers")
    try:
        handler = getattr(module, settings.handlers_mapping.get(handler_name))
    except AttributeError:
        return

    chat = get_chat(chat=update.effective_chat)

    # cleanup not answered reply_markups
    remove_last_markup(chat, context)

    if not hasattr(chat, "state"):
        try:
            initialize_state_if_not(chat=chat)
        except IndexError:
            update.message.reply_text("Извините, но админ не добавил вопросы :/\nНапишите ему, если хочется поиграть.")
            return

    handler(update, context, chat)


all_handler = CommandHandler(
    ['start', 'reg', 'unreg', 'participants', 'play', 'next', 'timer', 'reset', 'complexity'],
    handlers_dispatcher
)

button_handler = CallbackQueryHandler(button)

dispatcher.add_handler(all_handler)
dispatcher.add_handler(button_handler)
# updater.start_polling()
