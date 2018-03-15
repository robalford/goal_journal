import pytz
import random

from django.conf import settings
from django.test import TestCase, LiveServerTestCase
from django.urls import reverse

from selenium import webdriver
from selenium.webdriver.support.ui import Select

from goal_journal.users.models import User
from goal_journal.goals.models import Goal, Category, Action, ActionLog

TZ = pytz.timezone(settings.TIME_ZONE)


def create_goals_for_user(user):
    for i in range(5):
        new_goal = Goal(user=user, goal='Goal {}'.format(i))
        new_goal.save()
    user_goals = Goal.objects.filter(user=user)
    # some lists for building and adding goal data
    categories = ['Home', 'Health', 'Work']
    actions = ['Do hard stuff', 'Do hard things', 'Be less lazy']
    # add categories, actions and challenges to goals
    for goal in user_goals:
        category = Category(user=user, category=random.choice(categories))
        category.save()
        goal.categories.add(category)
        for i, a in enumerate(actions):
            a = a + str(i)  # make each action unique
            action = Action(user=user, action=a)
            action.save()
            goal.actions.add(action)
    return user_goals


class GoalTestCase(TestCase):
    def setUp(self):
        self.user = User(username='johndoe', email='johndoe@me.com')
        self.user.save()
        self.user_goals = create_goals_for_user(self.user)
        self.existing_goal = Goal.objects.filter(user=self.user).first()
        self.other_user = User(username='janedoe', email='janedoe@me.com')
        self.other_user.save()
        self.other_user_goals = create_goals_for_user(self.other_user)
        self.new_goal_url = reverse('goals:new_goal')
        self.new_category_url = reverse('goals:new_category')
        self.new_goal_data = {
             'actions-0-action': 'Stop being lazy',
             'actions-0-id': '',
             'actions-1-action': '',
             'actions-1-id': '',
             'actions-2-action': '',
             'actions-2-id': '',
             'actions-INITIAL_FORMS': '0',
             'actions-MAX_NUM_FORMS': '1000',
             'actions-MIN_NUM_FORMS': '0',
             'actions-TOTAL_FORMS': '3',
             'categories': '{}'.format(Category.objects.first().pk),
             'goal': 'Make my bed',
             'target_date': ''
        }
        self.edit_goal_url = reverse('goals:edit_goal', args=[self.existing_goal.pk])
        category_pk = self.existing_goal.categories.first().pk
        action_pks = [action.pk for action in self.existing_goal.actions.all()]
        self.edit_goal_data = {
            'actions-0-action': 'Do harder stuff',
            'actions-0-id': str(action_pks[0]),
            'actions-1-action': 'Do harder things',
            'actions-1-id': str(action_pks[1]),
            'actions-2-action': 'Be way less lazy',
            'actions-2-id': str(action_pks[2]),
            'actions-3-action': '',
            'actions-3-id': '',
            'actions-INITIAL_FORMS': '1',
            'actions-MAX_NUM_FORMS': '1000',
            'actions-MIN_NUM_FORMS': '0',
            'actions-TOTAL_FORMS': '4',
            'categories': str(category_pk),
            'goal': 'Lose 10 pounds',
            'target_date': ''
        }
        self.new_action_data = {
            'form-0-action': 'Get motivated',
            'form-0-id': '',
            'form-1-action': '',
            'form-1-id': '',
            'form-2-action': '',
            'form-2-id': '',
            'form-INITIAL_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'form-MIN_NUM_FORMS': '0',
            'form-TOTAL_FORMS': '3'
        }
        self.manage_action_data = {
            'action': 'Pick up my stuff',
            'goals': '{}'.format(Goal.objects.first().pk)
        }

    def test_user_can_create_new_goal(self):
        self.client.force_login(self.user)
        response = self.client.get(self.new_goal_url)
        self.assertContains(response, 'Set a new goal')
        response = self.client.post(self.new_goal_url, self.new_goal_data, follow=True)
        self.assertContains(response, 'You set a new goal! Start tracking your progress by recording your actions below.')
        self.assertContains(response, self.new_goal_data['goal'])

    def test_user_can_create_new_category(self):
        self.client.force_login(self.user)
        response = self.client.get(self.new_goal_url)
        self.assertContains(response, 'Set a new goal')
        response = self.client.post(self.new_category_url, {'category': 'Mountain climbing'}, follow=True)
        self.assertContains(response, 'Mountain climbing')

    def test_user_can_edit_existing_goal(self):
        self.client.force_login(self.user)
        response = self.client.get(self.edit_goal_url)
        self.assertContains(response, 'Edit goal')
        self.assertContains(response, self.existing_goal.goal)
        response = self.client.post(self.edit_goal_url, self.edit_goal_data, follow=True)
        self.assertContains(response, 'Your changes have been saved!')
        self.assertContains(response, self.edit_goal_data['goal'])
        self.assertNotContains(response, self.existing_goal.goal)

    def test_delete_goal(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('goals:delete_goal', args=[self.existing_goal.pk]), {},
                                    follow=True)
        self.assertContains(response, "You deleted the goal {}.".format(self.existing_goal.goal))

    def test_goal_list_displays_all_goals(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('goals:goal_list'))
        for goal in self.user_goals:
            self.assertContains(response, goal.goal)
            self.assertContains(response, '<a href="/goals/{}/">'.format(goal.pk))
            for category in goal.categories.all():
                self.assertContains(response, category)
        # test that we only display goals for this user
        for other_user_goal in self.other_user_goals:
            self.assertNotContains(response, '<a href="/goals/{}/">'.format(other_user_goal.pk))

    def test_goal_list_category_filter(self):
        self.client.force_login(self.user)
        category = Category.objects.first()
        response = self.client.get(reverse('goals:category', args=[category.pk]))
        for goal in self.user_goals:
            if category in goal.categories.all():
                self.assertContains(response, goal.goal)
            elif category not in goal.categories.all():
                self.assertNotContains(response, goal.goal)

    def test_goal_detail(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('goals:goal_detail', args=[self.existing_goal.pk]))
        self.assertContains(response, self.existing_goal.goal)
        for action in self.existing_goal.actions.all():
            self.assertContains(response, action.action)

    def test_add_new_action(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('goals:new_action', args=[self.existing_goal.pk]),
                                    self.new_action_data, follow=True)
        self.assertContains(response, 'Your actions for this goal have been updated.')
        self.assertContains(response, self.new_action_data['form-0-action'])

    def test_manage_action(self):
        action = self.existing_goal.actions.first()
        self.client.force_login(self.user)
        response = self.client.get(reverse('goals:manage_action', args=[self.existing_goal.pk, action.pk]))
        self.assertContains(response, action.action)
        for goal in action.goals.all():
            self.assertContains(response, goal.goal)
        response = self.client.post(reverse('goals:manage_action', args=[self.existing_goal.pk, action.pk]),
                                    self.manage_action_data, follow=True)
        self.assertContains(response, 'You updated your action for this goal')
        self.assertContains(response, self.manage_action_data['action'])
        # test completing action
        self.manage_action_data['action_completed'] = 'on'
        response = self.client.post(reverse('goals:manage_action', args=[self.existing_goal.pk, action.pk]),
                                    self.manage_action_data, follow=True)
        self.assertContains(response, 'Nice work! You completed one of your actions for this goal.')
        self.assertNotContains(response, action.action)
        action.refresh_from_db()
        self.assertEqual(action.action_completed, True)

    def test_delete_action(self):
        action = self.existing_goal.actions.first()
        self.client.force_login(self.user)
        response = self.client.post(reverse('goals:delete_action', args=[self.existing_goal.pk, action.pk]), {},
                                    follow=True)
        self.assertContains(response, "You deleted the action {} from {}.".format(
            action.action, self.existing_goal.goal))
        self.existing_goal.refresh_from_db()
        self.assertNotIn(action, self.existing_goal.actions.all())

    def test_action_log_list(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('goals:action_log_list', args=[self.existing_goal.pk]))
        for logged_action in ActionLog.objects.all():
            if logged_action.action.goals == self.existing_goal:
                self.assertContains(response,
                                    logged_action.status_logged.astimezone(TZ).strftime('%b. %-d, %Y, %-I:%M'))
            else:
                self.assertNotContains(response,
                                       logged_action.status_logged.astimezone(TZ).strftime('%b. %-d, %Y, %-I:%M'))


class ActionLogFrontEndTest(LiveServerTestCase):
    def setUp(self):
        # selenium
        self.browser = webdriver.Firefox()
        self.addCleanup(self.browser.quit)
        # user and goal data
        self.user = User(username='johndoe', email='johndoe@me.com')
        self.user.set_password('alksdjfkas')
        self.user.save()
        self.user_goals = create_goals_for_user(self.user)
        self.existing_goal = Goal.objects.first()

    def test_action_log_ajax(self):
        self.browser.get('{}{}'.format(
            self.live_server_url, reverse('goals:goal_detail', args=[self.existing_goal.pk])))
        self.browser.find_element_by_id('id_login').send_keys(self.user.username)
        self.browser.find_element_by_id('id_password').send_keys('alksdjfkas')
        self.browser.find_element_by_css_selector('button.btn.btn-primary').click()
        Select(self.browser.find_element_by_id("id_form-0-action_status")).select_by_visible_text('Success!')
        action_logged = ActionLog.objects.latest('status_logged')
        self.assertIn('<div id="action-{}-log"><p>\n    '
                      '<span class="badge badge-pill badge-success">Success!</span>'.format(action_logged.action.pk),
                      self.browser.page_source)
        self.assertIn(action_logged.status_logged.astimezone(TZ).strftime('%b. %-d, %Y %-I:%M'),
                      self.browser.page_source)
        Select(self.browser.find_element_by_id("id_form-1-action_status")).select_by_visible_text('WIP')
        action_logged = ActionLog.objects.latest('status_logged')
        self.assertIn('<div id="action-{}-log"><p>\n    '
                      '<span class="badge badge-pill badge-warning">WIP</span>'.format(action_logged.action.pk),
                      self.browser.page_source)
        self.assertIn(action_logged.status_logged.astimezone(TZ).strftime('%b. %-d, %Y %-I:%M'),
                      self.browser.page_source)
        Select(self.browser.find_element_by_id("id_form-2-action_status")).select_by_visible_text('Fail')
        action_logged = ActionLog.objects.latest('status_logged')
        self.assertIn('<div id="action-{}-log"><p>\n    '
                      '<span class="badge badge-pill badge-danger">Fail</span>'.format(action_logged.action.pk),
                      self.browser.page_source)
        self.assertIn(action_logged.status_logged.astimezone(TZ).strftime('%b. %-d, %Y %-I:%M'),
                      self.browser.page_source)



