from rest_framework import serializers

from goal_journal.goals.models import Category, Goal, GoalScore, Action, ActionLog
from goal_journal.journal.models import Entry


class CategorySerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = Category
        fields = '__all__'


class GoalSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    current_score = serializers.ReadOnlyField()
    actions = serializers.StringRelatedField(many=True)
    categories = serializers.StringRelatedField(many=True)

    class Meta:
        model = Goal
        fields = (
            'id',
            'user',
            'goal',
            'current_score',
            'date_created',
            'target_date',
            'categories',
            'actions',
            'goal_achieved',
        )


class GoalScoreSerializer(serializers.ModelSerializer):
    goal = serializers.StringRelatedField()

    class Meta:
        model = GoalScore
        fields = '__all__'


class ActionSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    goals = serializers.StringRelatedField(many=True)

    class Meta:
        model = Action
        fields = (
            'id',
            'user',
            'action',
            'goals',
            'priority',
            'action_completed',
        )


class ActionLogSerializer(serializers.ModelSerializer):
    action = serializers.StringRelatedField()

    class Meta:
        model = ActionLog
        fields = '__all__'


class JournalEntrySerializer(serializers.ModelSerializer):
    goal = serializers.StringRelatedField()

    class Meta:
        model = Entry
        fields = '__all__'
