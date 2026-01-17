from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EpicViewSet, UserStoryViewSet, TaskViewSet, GeneralStatisticsView
from .statistics_views import StatisticsViewSet

# Create router and register viewsets
router = DefaultRouter()
router.register(r'epics', EpicViewSet, basename='epic')
router.register(r'user-stories', UserStoryViewSet, basename='userstory')
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'statistics', StatisticsViewSet, basename='statistics')




urlpatterns = [
    path('', include(router.urls)),
]


# to include api view
# from django.urls import path, include
# from rest_framework.routers import DefaultRouter
# from rest_framework.response import Response
# from rest_framework.decorators import api_view
# from rest_framework.reverse import reverse
#
# from .views import EpicViewSet, UserStoryViewSet, TaskViewSet, GeneralStatisticsView
# from .statistics_views import StatisticsViewSet
#
#
# @api_view(['GET'])
# def api_root(request, format=None):
#     """
#     Custom API root view that includes APIView endpoints
#     """
#     return Response({
#         'epics': reverse('epic-list', request=request, format=format),
#         'user-stories': reverse('userstory-list', request=request, format=format),
#         'tasks': reverse('task-list', request=request, format=format),
#         'statistics': reverse('statistics-list', request=request, format=format),
#         'general-statistics': reverse('general-statistics', request=request, format=format),
#     })
#
#
# router = DefaultRouter()
# router.register(r'epics', EpicViewSet, basename='epic')
# router.register(r'user-stories', UserStoryViewSet, basename='userstory')
# router.register(r'tasks', TaskViewSet, basename='task')
# router.register(r'statistics', StatisticsViewSet, basename='statistics')
#
# urlpatterns = [
#     path('', api_root, name='api-root'),
#     # Custom root view
#     path('', include(router.urls)),
#     path('general-statistics/', GeneralStatisticsView.as_view(), name='general-statistics'),
# ]