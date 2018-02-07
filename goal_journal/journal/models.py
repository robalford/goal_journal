from django.db import models

from goal_journal.goals.models import Goal, Action
from goal_journal.users.models import User


class Entry(models.Model):
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE)
    progress = models.TextField()
    date_of_entry = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Entries'
        ordering = ['-date_of_entry', ]

    def __str__(self):
        return '{} {}'.format(self.goal, self.date_of_entry)
