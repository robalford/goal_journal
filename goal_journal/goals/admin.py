from django.contrib import admin

from .models import Category, Goal, GoalScore, Action, ActionLog

admin.site.register(Category)
admin.site.register(Goal)
admin.site.register(GoalScore)
admin.site.register(Action)
admin.site.register(ActionLog)
