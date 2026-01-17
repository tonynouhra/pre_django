from datetime import timezone

from django.db.models import Count
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView

from .models import Epic, UserStory, Task
from .serializers import (
    EpicSerializer,
    EpicListSerializer,
    UserStorySerializer,
    UserStoryListSerializer,
    TaskSerializer,
)


class EpicViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Epic model

    Provides:
    - list: GET /api/epics/
    - create: POST /api/epics/
    - retrieve: GET /api/epics/{id}/
    - update: PUT /api/epics/{id}/
    - partial_update: PATCH /api/epics/{id}/
    - destroy: DELETE /api/epics/{id}/
    """

    queryset = Epic.objects.all()
    serializer_class = EpicSerializer

    # Filtering, searching, ordering
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'owner', 'title']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'due_date', 'priority']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """Use simplified serializer for list view"""
        if self.action == 'list':
            return EpicListSerializer
        return EpicSerializer

    @action(detail=True, methods=['get'])
    def user_stories(self, request, pk=None):
        """
        Custom action: Get all user stories for this epic
        GET /api/epics/{id}/user_stories/
        """
        epic = self.get_object()
        user_stories = epic.user_stories.all()
        serializer = UserStoryListSerializer(user_stories, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        """Auto-set reporter to current user if not provided"""
        if 'reporter' not in serializer.validated_data or serializer.validated_data['reporter'] is None:
            serializer.save(reporter=self.request.user)
        else:
            serializer.save()


class UserStoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for UserStory model

    Provides CRUD operations for user stories
    """

    queryset = UserStory.objects.all()
    serializer_class = UserStorySerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'epic', 'assigned_to']
    search_fields = ['title', 'description', 'as_a', 'i_want', 'so_that']
    ordering_fields = ['created_at', 'due_date', 'priority', 'story_points']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """Use simplified serializer for list view"""
        if self.action == 'list':
            return UserStoryListSerializer
        return UserStorySerializer

    @action(detail=True, methods=['get'])
    def tasks(self, request, pk=None):
        """
        Custom action: Get all tasks for this user story
        GET /api/user-stories/{id}/tasks/
        """
        user_story = self.get_object()
        tasks = user_story.tasks.all()
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        """Auto-set reporter to current user if not provided"""
        if 'reporter' not in serializer.validated_data or serializer.validated_data['reporter'] is None:
            serializer.save(reporter=self.request.user)
        else:
            serializer.save()


class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Task model

    Provides CRUD operations for tasks
    """

    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'user_story', 'assigned_to']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'due_date', 'priority']
    ordering = ['-created_at']

    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """
        Custom action: Get all overdue tasks
        GET /api/tasks/overdue/
        """
        from django.utils import timezone
        overdue_tasks = Task.objects.filter(
            due_date__lt=timezone.now(),
            status__in=['TODO', 'IN_PROGRESS']
        )
        serializer = self.get_serializer(overdue_tasks, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get task statistics

        Endpoint: GET /api/tasks/statistics/

        Query params:
        - user_story: Filter by user story ID
        - epic: Filter by epic ID
        - assigned_to: Filter by user ID
        """
        # Start with all tasks
        queryset = self.queryset

        # Filter by query parameters
        user_story_id = request.query_params.get('user_story', None)
        epic_id = request.query_params.get('epic', None)
        assigned_to_id = request.query_params.get('assigned_to', None)

        if user_story_id:
            queryset = queryset.filter(user_story_id=user_story_id)

        if epic_id:
            queryset = queryset.filter(user_story__epic_id=epic_id)

        if assigned_to_id:
            queryset = queryset.filter(assigned_to_id=assigned_to_id)

            # Calculate statistics
        total_tasks = queryset.count()

        if total_tasks == 0:
            return Response({
                'total': 0,
                'message': 'No tasks found'
            })

            # Count by status
        status_counts = queryset.values('status').annotate(count=Count('id'))

        # Calculate percentages
        todo = queryset.filter(status='TODO').count()
        in_progress = queryset.filter(status='IN_PROGRESS').count()
        done = queryset.filter(status='DONE').count()
        blocked = queryset.filter(status='BLOCKED').count()
        cancelled = queryset.filter(status='CANCELLED').count()

        # Count overdue tasks
        overdue = queryset.filter(
            due_date__lt=timezone.now(),
            status__in=['TODO', 'IN_PROGRESS']
        ).count()

        # Priority distribution
        priority_counts = queryset.values('priority').annotate(count=Count('id'))

        return Response({
            'total': total_tasks,
            'by_status': {
                'TODO': {
                    'count': todo,
                    'percentage': round((todo / total_tasks) * 100, 2)
                },
                'IN_PROGRESS': {
                    'count': in_progress,
                    'percentage': round((in_progress / total_tasks) * 100, 2)
                },
                'DONE': {
                    'count': done,
                    'percentage': round((done / total_tasks) * 100, 2)
                },
                'BLOCKED': {
                    'count': blocked,
                    'percentage': round((blocked / total_tasks) * 100, 2)
                },
                'CANCELLED': {
                    'count': cancelled,
                    'percentage': round((cancelled / total_tasks) * 100, 2)
                }
            },
            'by_priority': [
                {
                    'priority': item['priority'],
                    'count': item['count'],
                    'percentage': round((item['count'] / total_tasks) * 100, 2)
                }
                for item in priority_counts
            ],
            'overdue': {
                'count': overdue,
                'percentage': round((overdue / total_tasks) * 100, 2)
            },
            'completion_rate': round((done / total_tasks) * 100, 2)
        })

    def perform_create(self, serializer):
        """Auto-set reporter to current user if not provided"""
        if 'reporter' not in serializer.validated_data or serializer.validated_data['reporter'] is None:
            serializer.save(reporter=self.request.user)
        else:
            serializer.save()


class GeneralStatisticsView(APIView):
    """
    General statistics endpoint

    Endpoint: GET /api/statisticsav/

    Query params:
    - type: 'task', 'user_story', or 'epic'
    - id: Optional ID to filter specific item's children
    """

    def list(self, request):
        """
        Overview of available statistics endpoints
        GET /api/statistics/
        """
        return Response({
            'message': 'StatisticsAV API',
            'available_endpoint': {
                '/api/statisticsav/'
            },
            'usage': {
                'type': "Specify 'type' as 'task', 'user_story', or 'epic'",
            }
        })

    def get(self, request):
        stat_type = request.query_params.get('type', 'task')
        item_id = request.query_params.get('id', None)

        if stat_type == 'task':
            return self.get_task_statistics(item_id)
        elif stat_type == 'user_story':
            return self.get_user_story_statistics(item_id)
        elif stat_type == 'epic':
            return self.get_epic_statistics(item_id)
        else:
            return Response({'error': 'Invalid type. Use: task, user_story, or epic'}, status=400)

    def get_task_statistics(self, user_story_id):
        queryset = Task.objects.all()
        if user_story_id:
            queryset = queryset.filter(user_story_id=user_story_id)

        total = queryset.count()
        if total == 0:
            return Response({'total': 0})

        done = queryset.filter(status='DONE').count()

        return Response({
            'type': 'task',
            'total': total,
            'done': done,
            'completion_rate': round((done / total) * 100, 2)
        })

    def get_user_story_statistics(self, epic_id):
        queryset = UserStory.objects.all()
        if epic_id:
            queryset = queryset.filter(epic_id=epic_id)

        total = queryset.count()
        if total == 0:
            return Response({'total': 0})

        done = queryset.filter(status='DONE').count()

        return Response({
            'type': 'user_story',
            'total': total,
            'done': done,
            'completion_rate': round((done / total) * 100, 2)
        })

    def get_epic_statistics(self, owner_id):
        queryset = Epic.objects.all()
        if owner_id:
            queryset = queryset.filter(owner_id=owner_id)

        total = queryset.count()
        if total == 0:
            return Response({'total': 0})

        done = queryset.filter(status='DONE').count()

        return Response({
            'type': 'epic',
            'total': total,
            'done': done,
            'completion_rate': round((done / total) * 100, 2)
        })
