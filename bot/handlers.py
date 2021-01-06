from telegram import Update
from telegram.ext import CallbackContext
from telegram.utils import helpers

from five_secs_django.main.models import User, UserScore, State, Chat
from bot.utils import get_chat, ask_next_user, ask_user, get_participants, send_markup_message, \
    get_next_user_id, mention_user
from bot.markups import get_next_button_markup, get_complexity_buttons_markup, get_participants_buttons_markup, \
    get_reset_buttons_markup


def start(update: Update, context: CallbackContext, chat: Chat) -> None:
    url = helpers.create_deep_linked_url(context.bot.get_me().username, "lets-play", group=True)
    message = """Как играть:
1. Зарегистрироваться каждому участнику командой /reg
2. После регистрации всех участников начать игру командой /play

Посмотреть всех участников и кол-во набранных очков: /participants
Вы можете сбросить счёт/отвеченные вопросы/зарегистрированных игроков командой /reset
Участников так же можно разрегистрировать командой /unreg

Хорошего настроения!

Добавь бота в пати-чат: %s""" % url
    update.message.reply_text(text=message)


# /reg
def register(update: Update, context: CallbackContext, chat: Chat) -> None:
    chat_id = chat.chat_id
    user = update.effective_user
    username = user["username"]
    user, _ = User.objects.update_or_create(telegram_id=user["id"],
                                            defaults={
                                                "username": username,
                                                "last_name": user["last_name"],
                                                "first_name": user["first_name"]
                                            })
    UserScore.objects.update_or_create(user=user, chat=chat, defaults={"score": 0})
    if user not in chat.registered_users.all():
        chat.registered_users.add(user)
        state = chat.state
        # if no user in state
        if not state.current_user:
            state.current_user = user
            state.started_from = user
            state.save()
        context.bot.send_message(chat_id=chat_id, text="%s зарегистрирован" % user.call_name)
    else:
        context.bot.send_message(chat_id=chat_id, text="%s уже зарегистрирован" % user.call_name)


# /unreg n
def unregister(update: Update, context: CallbackContext, chat: Chat) -> None:
    def get_fail_message(core_text):
        participants = get_participants(chat)
        if participants:
            message = core_text % participants
        else:
            message = "Участники не зарегистрированы. Зарегистрируйтесь командой /reg"
        return message

    participants_markup = get_participants_buttons_markup(chat)
    if participants_markup:
        send_markup_message(
            chat.state,
            update.message.reply_text,
            text="Выберите участника на исключение",
            reply_markup=participants_markup
        )
    else:
        update.message.reply_text("Участники не зарегистрированы. Зарегистрируйтесь командой /reg")

    # context.bot.send_message(chat_id=chat.chat_id, parse_mode="html", text=message)


# /participants
def participants(update: Update, context: CallbackContext, chat: Chat) -> None:
    message = "Никто не зарегистрирован"
    participants_text = get_participants(chat)
    if participants_text:
        message = "<b>Участники:</b>\n%s" % participants_text

    context.bot.send_message(chat_id=chat.chat_id, parse_mode="html", text=message)


def ask_next(update: Update, context: CallbackContext, chat: Chat) -> None:
    if not getattr(chat.state, "current_user"):
        update.message.reply_text("Используйте /reg для регистрации. После этого можно начать игру")
        return
    state = chat.state
    if state.game_started:
        ask_next_user(chat, context.bot)
    else:
        state.game_started = True
        state.started_from = state.current_user
        state.save()
        ask_user(chat, context.bot)


def play(*args, **kwargs) -> None:
    # wrapper for better UX
    # play or next works same
    ask_next(*args, **kwargs)


def timer(update: Update, context: CallbackContext, chat: Chat) -> None:
    interval = update.message["text"]
    try:
        interval = int(interval.split('/timer ')[1])
        chat.answer_interval = interval
        chat.save()
        message = "Интервал %s секунд сохранён" % interval
    except (ValueError, IndexError):
        message = "Интервал должен быть числом, пример: /timer 5"

    context.bot.send_message(chat_id=chat.chat_id, text=message)


def set_complexity(update: Update, context: CallbackContext, chat: Chat) -> None:
    chat_id = update.effective_chat.id
    chat = get_chat(chat_id=chat_id)
    send_markup_message(
        chat.state,
        update.message.reply_text,
        text="Выбери уровень сложности вопросов",
        reply_markup=get_complexity_buttons_markup()
    )


def reset(update: Update, context: CallbackContext, chat: Chat) -> None:
    chat_id = update.effective_chat.id
    chat = get_chat(chat_id=chat_id)
    send_markup_message(
        chat.state,
        update.message.reply_text,
        text="Выберите, что мне сбросить",
        reply_markup=get_reset_buttons_markup()
    )


def button(update: Update, context: CallbackContext) -> None:
    # TODO make segmentation
    query = update.callback_query
    chat_id = update.effective_chat["id"]
    chat = get_chat(chat_id=chat_id)
    query.answer()
    response = query.data

    if response.startswith("reset_"):
        if response == "reset_score":
            UserScore.objects.filter(chat=chat).update(score=0)
            message = "Счёт сброшен"
        elif response == "reset_participants":
            chat.registered_users.clear()
            State.objects.get(chat=chat).delete()
            message = "Участники сброшены"
        elif response == "reset_questions":
            chat.answered_questions.clear()
            message = "Отвеченные вопросы сброшены"
        elif response == "reset_all":
            UserScore.objects.filter(chat=chat).update(score=0)
            chat.registered_users.clear()
            State.objects.get(chat=chat).delete()
            chat.answered_questions.clear()
            message = "Сбросил всё, фух.."
        query.edit_message_text(text=message, reply_markup=None)
    elif response.startswith("complexity_"):
        complexity_level = Chat.COMPLEXITY_LEVELS.get(response)
        chat.complexity_level = complexity_level[0]
        chat.save()
        query.edit_message_text(text="Выбраны " + complexity_level[1].lower() + " вопросы", reply_markup=None)
    elif response.startswith("unregister_"):
        participant_id = response.split('_')[1]
        user = User.objects.get(pk=participant_id)
        chat.registered_users.remove(user)
        first_registered = chat.registered_users.first()
        state = chat.state
        if state.current_user != user:
            pass
        elif not first_registered:
            state.current_user = None
            state.started_from = None
        else:
            state.current_user = first_registered
            state.started_from = first_registered
        state.save()

        query.edit_message_text(text="%s исключён" % user.call_name, reply_markup=None)
    elif response.startswith("question_"):
        state = State.objects.get(chat=chat)
        user = state.current_user
        score = user.score.filter(chat=chat).first()
        if response == "question_answered":
            score.score += 1
            score.save()
            chat.answered_questions.add(state.current_question)
            state.current_question = None
            state.started_from = None
            state.save()
            send_markup_message(
                state,
                query.edit_message_text,
                text=f"Отлично, %s, у тебя %s очков" % (user.call_name, score.score),
                reply_markup=get_next_button_markup()
            )
        elif response == "question_failed":
            query.delete_message()
            started_from = state.started_from
            next_user_id = get_next_user_id(chat)
            if started_from and next_user_id == started_from.id:
                score = started_from.score.filter(chat=chat).first()
                score.score += 1
                score.save()
                chat.answered_questions.add(state.current_question)
                state.current_user_id = next_user_id
                state.current_question = None
                state.started_from = None
                state.save()
                answer_body = {
                    "parse_mode": "html",
                    "text": mention_user(started_from,
                                         "Никто не ответил, ты получаешь +1 очко!\nУ тебя %s" % score.score),
                    "reply_markup": get_next_button_markup()
                }
                send_markup_message(state, context.bot.send_message, chat_id=chat.chat_id, **answer_body)
            else:
                ask_next_user(chat, context.bot)
    elif response == "next":
        query.edit_message_reply_markup(reply_markup=None)
        ask_next(update, context, chat)
