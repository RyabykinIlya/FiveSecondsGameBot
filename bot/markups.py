from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from five_secs_django.main.models import Chat
from bot import settings


def split_markup_buttons(buttons, inline_count=2):
    keyboard = []
    tmp = []
    count = 0
    for button in buttons:
        count += 1
        tmp.append(button)
        if count == inline_count:
            keyboard.append(tmp.copy())
            tmp.clear()
            count = 0
    if tmp:
        keyboard.append(tmp)

    return keyboard


def get_answer_buttons_markup():
    keyboard = [
        [
            InlineKeyboardButton("Да", callback_data='question_answered'),
            InlineKeyboardButton("Нет", callback_data='question_failed'),
        ],
    ]

    return InlineKeyboardMarkup(keyboard)


def get_next_button_markup():
    keyboard = [
        [
            InlineKeyboardButton("Далее", callback_data='next'),
        ],
    ]

    return InlineKeyboardMarkup(keyboard)


def get_complexity_buttons_markup():
    COMPLEXITY_LEVELS = Chat.COMPLEXITY_LEVELS
    buttons = []
    for name, level in COMPLEXITY_LEVELS.items():
        buttons.append(InlineKeyboardButton(level[1], callback_data=name))

    return InlineKeyboardMarkup(split_markup_buttons(buttons))


def get_reset_buttons_markup():
    reset_callback_mapping = settings.reset_callback_mapping
    buttons = []
    for name, value in reset_callback_mapping.items():
        buttons.append(InlineKeyboardButton(value, callback_data=name))

    return InlineKeyboardMarkup(split_markup_buttons(buttons, inline_count=3))


def get_participants_buttons_markup(chat):
    from bot.utils import get_participants
    participants_list = get_participants(chat=chat, as_list=True)
    if not participants_list:
        return None
    buttons = []
    for participant in participants_list:
        buttons.append(InlineKeyboardButton(participant[1], callback_data='unregister_%s' % participant[0]))

    return InlineKeyboardMarkup([buttons])
