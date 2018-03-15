from django.test import TestCase
from django.urls import reverse

from goal_journal.goals.models import Goal
from goal_journal.goals.tests import create_goals_for_user
from goal_journal.journal.models import Entry
from goal_journal.users.models import User


class JournalEntryTestCase(TestCase):

    def setUp(self):
        self.user = User(username='johndoe', email='johndoe@me.com')
        self.user.save()
        self.user_goals = create_goals_for_user(self.user)
        self.existing_goal = Goal.objects.filter(user=self.user).first()
        self.other_user = User(username='janedoe', email='janedoe@me.com')
        self.other_user.save()
        self.other_user_goals = create_goals_for_user(self.other_user)
        self.all_goals = list(self.user_goals) + list(self.other_user_goals)
        # create some journal entries for each goal
        for goal in self.all_goals:
            for i in range(5):
                entry = Entry(goal=goal, progress='My progress journal entry {} for goal {}'.format(
                    i, goal.goal)
                )
                entry.save()
        self.new_entry_url = reverse('journal:new_entry', args=[self.existing_goal.pk])
        self.user_entries = Entry.objects.filter(goal__user=self.user)
        self.other_user_entries = Entry.objects.filter(goal__user=self.other_user)
        self.new_entry_data = {
            'goal': self.existing_goal.pk,
            'progress': 'Not much progress',
        }
        self.edit_entry_data = {
            'goal': self.existing_goal.pk,
            'progress': 'Not much progress today',
        }

    def test_create_new_journal_entry(self):
        self.client.force_login(self.user)
        response = self.client.post(self.new_entry_url, self.new_entry_data, follow=True)
        self.assertContains(response, 'You created a new entry in your goal journal.')
        self.assertContains(response, self.new_entry_data['progress'])

    def test_edit_entry(self):
        entry = self.existing_goal.entry_set.last()
        self.client.force_login(self.user)
        response = self.client.get(reverse('journal:edit_entry', args=[entry.pk]))
        self.assertContains(response, entry.progress)
        self.assertContains(response, 'Edit journal entry for {}'.format(self.existing_goal.goal))
        response = self.client.post(reverse('journal:edit_entry', args=[entry.pk]),
                                    self.edit_entry_data, follow=True)
        self.assertContains(response, 'You updated an entry in your goal journal for {}.'.format(entry.goal.goal))
        entry.refresh_from_db()
        self.assertEqual(entry.progress, self.edit_entry_data['progress'])

    def test_delete_entry(self):
        entry = Entry.objects.last()
        self.client.force_login(self.user)
        response = self.client.post(reverse('journal:delete_entry', args=[entry.pk]), {},
                                    follow=True)
        self.assertContains(response, "You deleted the entry")
        self.existing_goal.refresh_from_db()
        self.assertNotIn(entry, self.existing_goal.entry_set.all())

    def test_journal_list_displays_all_entries(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('journal:goal_journal'))
        for entry in self.user_entries[:10]:  # first ten entries on the first page
            self.assertContains(response, entry.progress)
        # only display entries for the current user
        for other_user_entry in self.other_user_entries:
            self.assertNotContains(response, '<a href="/goal-journal/entry/{}/edit/">'.format(other_user_entry.pk))




