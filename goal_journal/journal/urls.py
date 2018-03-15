from django.conf.urls import url


from . import views

urlpatterns = [
    url(r'^$', views.goal_journal_view, name='goal_journal'),
    url(r'^goals/(?P<goal_pk>\d+)/entries/new/$', views.new_entry_view, name='new_entry'),
    url(r'^entries/(?P<entry_pk>\d+)/edit/$', views.edit_entry_view, name='edit_entry'),
    url(r'^entries/(?P<entry_pk>\d+)/delete/$', views.delete_entry_view, name='delete_entry'),
]
