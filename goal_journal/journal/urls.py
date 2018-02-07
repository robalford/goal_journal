from django.conf.urls import url


from . import views

urlpatterns = [
    url(r'^$', views.goal_journal_view, name='goal_journal'),
    url(r'^goal-filter/(?P<goal_pk>\d+)/$', views.goal_journal_view, name='goal_filter'),
    url(r'^entry/new/$', views.new_entry_view, name='new_entry'),
    url(r'^entry/(?P<entry_pk>\d+)/edit/$', views.edit_entry_view, name='edit_entry'),
    url(r'^entry/(?P<entry_pk>\d+)/delete/$', views.delete_entry_view, name='delete_entry'),
]
