from rest_framework import viewsets

from goal_journal.api.serializers import (CategorySerializer, GoalSerializer, GoalScoreSerializer,
                                          ActionSerializer, ActionLogSerializer, JournalEntrySerializer)
from goal_journal.goals.models import Category, Goal, GoalScore, Action, ActionLog
from goal_journal.journal.models import Entry

from rest_framework import permissions


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class GoalViewSet(viewsets.ModelViewSet):
    serializer_class = GoalSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )

    def get_queryset(self):
        return Goal.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class GoalScoreViewSet(viewsets.ModelViewSet):
    serializer_class = GoalScoreSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )

    def get_queryset(self):
        return GoalScore.objects.filter(goal__user=self.request.user)


class ActionViewSet(viewsets.ModelViewSet):
    serializer_class = ActionSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )

    def get_queryset(self):
        return Action.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ActionLogViewSet(viewsets.ModelViewSet):
    serializer_class = ActionLogSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )

    def get_queryset(self):
        return ActionLog.objects.filter(action__user=self.request.user)


class JournalEntryViewSet(viewsets.ModelViewSet):
    serializer_class = JournalEntrySerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )

    def get_queryset(self):
        return Entry.objects.filter(goal__user=self.request.user)
