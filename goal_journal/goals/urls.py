from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.goals_list_view, name='goal_list'),
    url(r'^(?P<goal_pk>\d+)/$', views.goal_detail_view, name='goal_detail'),
    url(r'^category/(?P<category_pk>\d+)/$', views.goals_list_view, name='category'),
    url(r'^new/$', views.new_goal_view, name='new_goal'),
    url(r'^category/new/$', views.new_category_view, name='new_category'),
    url(r'^(?P<pk>\d+)/edit/$', views.edit_goal_view, name='edit_goal'),
    url(r'^(?P<pk>\d+)/delete/$', views.delete_goal_view, name='delete_goal'),
    url(r'^(?P<pk>\d+)/goal-achieved/$', views.goal_achieved_view, name='goal_achieved'),
    url(r'^(?P<goal_pk>\d+)/actions/new/$', views.new_action_view, name='new_action'),
    url(r'^(?P<goal_pk>\d+)/actions/(?P<action_pk>\d+)$', views.manage_action_view, name='manage_action'),
    url(r'^(?P<goal_pk>\d+)/actions/(?P<action_pk>\d+)/delete/$', views.delete_action_view, name='delete_action'),
    url(r'^(?P<goal_pk>\d+)/action-log-list/$', views.action_log_list_view, name='action_log_list'),
    url(r'^(?P<goal_pk>\d+)/action-log/$', views.action_log_view, name='action_log'),
]
