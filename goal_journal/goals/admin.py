from django.contrib import admin

from .models import Category, Goal, Action

admin.site.register(Category)
admin.site.register(Goal)
admin.site.register(Action)
