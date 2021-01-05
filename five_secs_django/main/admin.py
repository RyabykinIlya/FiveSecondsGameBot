from django.contrib import admin

from five_secs_django.main.models import User, FiveSecQuestion, Chat, State, UserScore


class UserAdmin(admin.ModelAdmin):
    list_display = [field.name for field in User._meta.fields]


class FiveSecQuestionAdmin(admin.ModelAdmin):
    list_display = [field.name for field in FiveSecQuestion._meta.fields]


class ChatAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Chat._meta.fields]


class StateAdmin(admin.ModelAdmin):
    list_display = [field.name for field in State._meta.fields]


class UserScoreAdmin(admin.ModelAdmin):
    list_display = [field.name for field in UserScore._meta.fields]


admin.site.register(User, UserAdmin)
admin.site.register(FiveSecQuestion, FiveSecQuestionAdmin)
admin.site.register(Chat, ChatAdmin)
admin.site.register(State, StateAdmin)
admin.site.register(UserScore, UserScoreAdmin)
