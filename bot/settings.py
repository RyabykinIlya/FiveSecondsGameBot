import os

TOKEN = os.environ.get("BOT_TOKEN")

handlers_mapping = {
    "start": "start",
    "reg": "register",
    "unreg": "unregister",
    "participants": "participants",
    "play": "play",
    "next": "ask_next",
    "timer": "timer",
    "complexity": "set_complexity",
    "reset": "reset"
}

reset_callback_mapping = {
    "reset_score": "Счёт",
    "reset_participants": "Участников",
    "reset_questions": "Отвеченные вопросы",
    "reset_all": "Всё",
}
