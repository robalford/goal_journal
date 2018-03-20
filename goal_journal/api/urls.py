from django.conf.urls import url, include
from rest_framework import routers
from goal_journal.api import views

router = routers.DefaultRouter()
router.register(r'goals', views.GoalViewSet, base_name='goal')
router.register(r'goal-scores', views.GoalScoreViewSet, base_name='goal-score')
router.register(r'categories', views.CategoryViewSet, base_name='category')
router.register(r'actions', views.ActionViewSet, base_name='action')
router.register(r'action-logs', views.ActionLogViewSet, base_name='action-log')
router.register(r'entries', views.JournalEntryViewSet, base_name='entry')

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
