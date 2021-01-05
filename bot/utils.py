from django.contrib.auth import get_user_model

from telegram.error import BadRequest
from time import sleep
import random

from bot.markups import get_answer_buttons_markup
from five_secs_django.main.models import Chat, FiveSecQuestion, State

User = get_user_model()


def get_participants(chat, as_list=False):
    participants = chat.registered_users.all().prefetch_related('score').filter(score__chat=chat).values_list('id',
                                                                                                              'call_name',
                                                                                                              'score__score')
    if participants and not as_list:
        return '\n'.join(["%s (%s очков)" % (call_name, score) for id, call_name, score in participants])
    elif participants and as_list:
        return participants


def get_chat(chat_id):
    return (
        Chat.objects
            .prefetch_related("registered_users", "answered_questions", "state", "score")
            .get_or_create(chat_id=chat_id)
    )


# def get_question(chat):
#     return FiveSecQuestion.objects.all().exclude(pk__in=chat.answered_questions.all()).first()


def get_random_question(chat):
    complexity_level = chat.complexity_level
    # any questions
    if complexity_level == 0:
        return random.choice(
            FiveSecQuestion.objects
                .exclude(pk__in=chat.answered_questions.all())
        )
    else:
        return random.choice(
            FiveSecQuestion.objects
                .filter(complexity_level=complexity_level)
                .exclude(pk__in=chat.answered_questions.all())
        )


def initialize_state_if_not(chat):
    try:
        State.objects.get(chat=chat)
    except State.DoesNotExist:
        state = State.objects.create(chat=chat)
        question = get_random_question(chat=chat)
        state.current_question = question
        state.save()


def start_counting(chat, bot):
    # TODO make timer here https://raw.githubusercontent.com/python-telegram-bot/python-telegram-bot/master/examples/timerbot.py
    chat_id = chat.chat_id
    message_id = bot.send_message(chat_id=chat_id, text="...")['message_id']
    sleep(chat.answer_interval)

    reply_markup = get_answer_buttons_markup()
    send_markup_message(chat.state, bot.edit_message_text, chat_id=chat_id, message_id=message_id, text="Ответил?",
                        reply_markup=reply_markup)


def remove_last_markup(chat, context):
    try:
        if hasattr(chat, "state"):
            last_markup_mes_id = chat.state.last_markup_message_id
            if last_markup_mes_id:
                context.bot.edit_message_reply_markup(chat_id=chat.chat_id, message_id=last_markup_mes_id,
                                                      reply_markup=None)
                chat.state.last_markup_message_id = None
                chat.state.save()
    except BadRequest:
        pass


def send_markup_message(state, func, **kwargs):
    # control markup messages and remove them if any command interrupted normal bot work
    message = func(**kwargs)
    state.last_markup_message_id = message["message_id"]
    state.save()


def mention_user(user, message):
    return '<a href="tg://user?id=%s">%s</a>, %s' % (user.telegram_id, user.call_name, message)


def ask_user(chat, bot):
    state = chat.state
    question = state.current_question
    if question.complexity_level == 1:
        # yellow circle
        message_prepend = "\U0001F7E1 <i>" + str(question.id) + " (лёгкий)</i>.\n"
    else:
        # red circle
        message_prepend = "\U0001F534 <i>" + str(question.id) + " (сложный)</i>.\n"
    bot.send_message(chat_id=chat.chat_id, parse_mode="html",
                     text=message_prepend + mention_user(state.current_user, question.question_text))
    start_counting(chat, bot)


def get_next_user_id(chat):
    users_id = list(chat.registered_users.values_list("id", flat=True))
    try:
        cur_index = users_id.index(chat.state.current_user.id)
        return users_id[cur_index + 1]
    except IndexError:
        return users_id[0]


def ask_next_user(chat, bot):
    state = chat.state
    if not state.current_question:
        state.current_question = get_random_question(chat=chat)
        state.save()

    next_participant = User.objects.get(pk=get_next_user_id(chat))
    state.current_user = next_participant
    state.save()
    if not state.started_from:
        state.started_from = next_participant
        state.current_user = next_participant
        state.save()

    ask_user(chat, bot)
