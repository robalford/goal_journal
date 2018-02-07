from django.db import models

from goal_journal.users.models import User
from . import choices


class Category(models.Model):
    user = models.ForeignKey(User)
    category = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.category


class Goal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    goal = models.TextField()
    date_created = models.DateTimeField(auto_now=True)
    categories = models.ManyToManyField(Category, related_name='goals')
    actions = models.ManyToManyField('Action', related_name='goals')
    target_date = models.DateField(null=True, blank=True)
    goal_achieved = models.BooleanField(default=False)

    def __str__(self):
        return self.goal


class Action(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.TextField(blank=True)
    priority = models.SmallIntegerField(blank=True, null=True)
    action_completed = models.BooleanField(default=False)

    class Meta:
        ordering = ['priority', ]

    def __str__(self):
        return self.action


class ActionLog(models.Model):
    action = models.ForeignKey(Action, on_delete=models.CASCADE, null=True)
    action_status = models.IntegerField(choices=choices.ACTION_STATUS, blank=True, null=True)
    status_logged = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-status_logged', ]

    def __str__(self):
        return '{}: {} on {}'.format(self.action_status, self.action, self.status_logged)

    def get_action_status_class(self):
        if self.action_status == 0:
            bootstrap_class = 'danger'
        elif self.action_status == 5:
            bootstrap_class = 'warning'
        else:
            bootstrap_class = 'success'
        return bootstrap_class