from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action


from .models import Task, UserStory, Epic


class StatisticsViewSet(viewsets.ViewSet):
    """
    Statistics endpoints
    """

    def list(self, request):
        """
        Overview of available statistics endpoints
        GET /api/statistics/
        """
        return Response({
            'message': 'Statistics API',
            'available_endpoints': {
                'tasks': '/api/statistics/tasks/',
                'user_stories': '/api/statistics/user-stories/',
                'epics': '/api/statistics/epics/',
            },
            'usage': {
                'tasks': 'Get task statistics. Supports filters: ?user_story=ID, ?epic=ID, ?assigned_to=ID',
                'user_stories': 'Get user story statistics. Supports filters: ?epic=ID, ?assigned_to=ID',
                'epics': 'Get epic statistics. Supports filter: ?owner=ID'
            }
        })

    @action(detail=False, methods=['get'], url_path='tasks')
    def tasks(self, request):
        """                                                                                                                                                                                                                      
        Task statistics                                                                                                                                                                                                          
        GET /api/statistics/tasks/                                                                                                                                                                                               

        Query params:                                                                                                                                                                                                            
        - user_story: Filter by user story ID                                                                                                                                                                                    
        - epic: Filter by epic ID                                                                                                                                                                                                
        - assigned_to: Filter by user ID                                                                                                                                                                                         
        """
        queryset = Task.objects.all()

        # Filter by query params                                                                                                                                                                                                 
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
        total = queryset.count()

        if total == 0:
            return Response({
                'total': 0,
                'message': 'No tasks found'
            })

            # Count by status
        todo = queryset.filter(status='TODO').count()
        in_progress = queryset.filter(status='IN_PROGRESS').count()
        done = queryset.filter(status='DONE').count()
        blocked = queryset.filter(status='BLOCKED').count()

        return Response({
            'total': total,
            'by_status': {
                'TODO': {
                    'count': todo,
                    'percentage': round((todo / total) * 100, 2)
                },
                'IN_PROGRESS': {
                    'count': in_progress,
                    'percentage': round((in_progress / total) * 100, 2)
                },
                'DONE': {
                    'count': done,
                    'percentage': round((done / total) * 100, 2)
                },
                'BLOCKED': {
                    'count': blocked,
                    'percentage': round((blocked / total) * 100, 2)
                }
            },
            'completion_rate': round((done / total) * 100, 2)
        })

    @action(detail=False, methods=['get'], url_path='user-stories')
    def user_stories(self, request):
        """                                                                                                                                                                                                                      
        User Story statistics                                                                                                                                                                                                    
        GET /api/statistics/user-stories/                                                                                                                                                                                        

        Query params:                                                                                                                                                                                                            
        - epic: Filter by epic ID                                                                                                                                                                                                
        - assigned_to: Filter by user ID                                                                                                                                                                                         
        """
        queryset = UserStory.objects.all()

        epic_id = request.query_params.get('epic', None)
        assigned_to_id = request.query_params.get('assigned_to', None)

        if epic_id:
            queryset = queryset.filter(epic_id=epic_id)

        if assigned_to_id:
            queryset = queryset.filter(assigned_to_id=assigned_to_id)

        total = queryset.count()

        if total == 0:
            return Response({
                'total': 0,
                'message': 'No user stories found'
            })

        done = queryset.filter(status='DONE').count()
        in_progress = queryset.filter(status='IN_PROGRESS').count()
        todo = queryset.filter(status='TODO').count()

        return Response({
            'total': total,
            'by_status': {
                'TODO': {
                    'count': todo,
                    'percentage': round((todo / total) * 100, 2)
                },
                'IN_PROGRESS': {
                    'count': in_progress,
                    'percentage': round((in_progress / total) * 100, 2)
                },
                'DONE': {
                    'count': done,
                    'percentage': round((done / total) * 100, 2)
                }
            },
            'completion_rate': round((done / total) * 100, 2)
        })

    @action(detail=False, methods=['get'], url_path='epics')
    def epics(self, request):
        """                                                                                                                                                                                                                      
        Epic statistics                                                                                                                                                                                                          
        GET /api/statistics/epics/                                                                                                                                                                                               

        Query params:                                                                                                                                                                                                            
        - owner: Filter by owner ID                                                                                                                                                                                              
        """
        queryset = Epic.objects.all()

        owner_id = request.query_params.get('owner', None)

        if owner_id:
            queryset = queryset.filter(owner_id=owner_id)

        total = queryset.count()

        if total == 0:
            return Response({
                'total': 0,
                'message': 'No epics found'
            })

        done = queryset.filter(status='DONE').count()
        in_progress = queryset.filter(status='IN_PROGRESS').count()
        todo = queryset.filter(status='TODO').count()

        return Response({
            'total': total,
            'by_status': {
                'TODO': {
                    'count': todo,
                    'percentage': round((todo / total) * 100, 2)
                },
                'IN_PROGRESS': {
                    'count': in_progress,
                    'percentage': round((in_progress / total) * 100, 2)
                },
                'DONE': {
                    'count': done,
                    'percentage': round((done / total) * 100, 2)
                }
            },
            'completion_rate': round((done / total) * 100, 2)
        })     