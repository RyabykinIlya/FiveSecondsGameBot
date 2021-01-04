from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.contrib.auth import get_user_model


class User(AbstractUser):
    telegram_id = models.IntegerField(null=True)
    language_code = models.CharField(max_length=10, null=True)
    registration_date = models.DateTimeField(default=timezone.now)


class FiveSecQuestion(models.Model):
    LANGUAGES = (("ru", "ru"), ("en", "en"))
    question_text = models.TextField()
    question_language = models.CharField(max_length=10, choices=LANGUAGES, default="ru")
    complexity_level = models.PositiveSmallIntegerField(default=1)

    class Meta:
        unique_together = ("question_text", "question_language")


class Chat(models.Model):
    chat_id = models.IntegerField()
    registered_users = models.ManyToManyField(get_user_model(), related_name="chats")
    answered_questions = models.ManyToManyField(FiveSecQuestion, related_name="chats")
    answer_interval = models.PositiveSmallIntegerField(default=5)
    # 0 - any complexity
    complexity_level = models.PositiveSmallIntegerField(default=0)

    COMPLEXITY_LEVELS = {
        "complexity_hard": (2, "Сложные"),
        "complexity_easy": (1, "Лёгкие"),
        "complexity_any": (0, "Любые")
    }


class State(models.Model):
    chat = models.OneToOneField(Chat, on_delete=models.CASCADE, related_name="state")
    current_user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="state_current",
                                     null=True)
    started_from = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="state_started_from",
                                     null=True)
    current_question = models.ForeignKey(FiveSecQuestion, on_delete=models.CASCADE, null=True)
    last_markup_message_id = models.SmallIntegerField(null=True)
    game_started = models.BooleanField(default=False)
    updated = models.DateTimeField(default=timezone.now)


class UserScore(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="score")
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="score")
    score = models.PositiveSmallIntegerField(default=0)
