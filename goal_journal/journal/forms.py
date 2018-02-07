from django import forms

from goal_journal.goals.models import Goal
from .models import Entry


class EntryForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        current_user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['goal'].queryset = Goal.objects.filter(user=current_user)

    class Meta:
        model = Entry
        fields = [
            'goal',
            'progress',
        ]
