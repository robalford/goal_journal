from django import forms

from .models import Goal, Category, Action, ActionLog


class GoalForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        current_user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['categories'].queryset = Category.objects.filter(user=current_user)

    class Meta:
        model = Goal
        fields = [
            'goal',
            'categories',
            'target_date',
        ]
        widgets = {
            'goal': forms.Textarea(attrs={'rows': 4}),
        }


class NewCategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category']


class ActionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        current_user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['goals'] = forms.ModelMultipleChoiceField(queryset=Goal.objects.filter(user=current_user))
        self.fields['goals'].required = False

    class Meta:
        model = Action
        fields = [
            'action',
            'priority',
            'action_completed',
        ]


ActionFormSet = forms.modelformset_factory(Action,
                                           fields=('action', ),
                                           widgets={'action': forms.Textarea(attrs={'rows': 4})},
                                           extra=3)


class ActionLogForm(forms.ModelForm):

    class Meta:
        model = ActionLog
        fields = [
            'action',
            'action_status',
        ]
        widgets = {'action': forms.HiddenInput}

