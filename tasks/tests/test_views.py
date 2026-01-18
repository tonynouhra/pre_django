"""
API endpoint tests for tasks app ViewSets.

Tests for:
- TaskViewSet: CRUD operations, overdue tasks, statistics
- UserStoryViewSet: CRUD operations, tasks list
- EpicViewSet: CRUD operations, user stories list
"""

import pytest
from django.urls import reverse
from rest_framework import status
from django.utils import timezone
from datetime import timedelta

from tasks.models import Epic, UserStory, Task
from tasks.tests.factories import UserFactory, EpicFactory, UserStoryFactory, TaskFactory


# ============================================================================
# TASK VIEWSET TESTS
# ============================================================================

@pytest.mark.django_db
class TestTaskViewSet:
    """Test suite for TaskViewSet API endpoints"""

    def test_list_tasks_requires_authentication(self, api_client):
        """Test listing tasks requires authentication"""
        url = reverse('task-list')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_tasks_authenticated(self, authenticated_client):
        """Test authenticated user can list tasks"""
        TaskFactory.create_batch(3)
        url = reverse('task-list')

        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 3

    def test_create_task(self, authenticated_client):
        """Test creating a task via API"""
        user_story = UserStoryFactory()
        url = reverse('task-list')
        data = {
            'title': 'New Task',
            'description': 'Task description',
            'user_story': user_story.id,
            'status': 'TODO',
            'priority': 'HIGH'
        }

        response = authenticated_client.post(url, data)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == 'New Task'
        assert response.data['priority'] == 'HIGH'
        assert Task.objects.filter(title='New Task').exists()

    def test_retrieve_task(self, authenticated_client):
        """Test retrieving a single task"""
        task = TaskFactory(title='Test Task')
        url = reverse('task-detail', kwargs={'pk': task.id})

        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == 'Test Task'
        assert response.data['id'] == task.id

    def test_update_task(self, authenticated_client):
        """Test updating a task via PUT"""
        task = TaskFactory(title='Old Title', status='TODO')
        url = reverse('task-detail', kwargs={'pk': task.id})
        data = {
            'title': 'Updated Title',
            'description': task.description,
            'user_story': task.user_story.id,
            'status': 'IN_PROGRESS',
            'priority': task.priority
        }

        response = authenticated_client.put(url, data)

        assert response.status_code == status.HTTP_200_OK
        task.refresh_from_db()
        assert task.title == 'Updated Title'
        assert task.status == 'IN_PROGRESS'

    def test_partial_update_task(self, authenticated_client):
        """Test partially updating a task via PATCH"""
        task = TaskFactory(status='TODO')
        url = reverse('task-detail', kwargs={'pk': task.id})
        data = {'status': 'DONE'}

        response = authenticated_client.patch(url, data)

        assert response.status_code == status.HTTP_200_OK
        task.refresh_from_db()
        assert task.status == 'DONE'

    def test_delete_task(self, authenticated_client):
        """Test deleting a task"""
        task = TaskFactory()
        url = reverse('task-detail', kwargs={'pk': task.id})

        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Task.objects.filter(id=task.id).exists()

    def test_overdue_tasks_endpoint(self, authenticated_client):
        """Test custom overdue tasks endpoint"""
        # Create overdue task
        past_date = timezone.now() - timedelta(days=5)
        overdue_task = TaskFactory(due_date=past_date, status='IN_PROGRESS')

        # Create non-overdue task
        future_date = timezone.now() + timedelta(days=5)
        TaskFactory(due_date=future_date, status='TODO')

        url = reverse('task-overdue')

        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
        # Check that overdue task is in results
        task_ids = [task['id'] for task in response.data]
        assert overdue_task.id in task_ids

    def test_task_statistics_endpoint(self, authenticated_client):
        """Test task statistics endpoint"""
        # Create tasks with different statuses
        TaskFactory.create_batch(2, status='TODO')
        TaskFactory.create_batch(3, status='DONE')
        TaskFactory(status='IN_PROGRESS')

        url = reverse('task-statistics')

        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['total'] == 6
        assert response.data['by_status']['TODO']['count'] == 2
        assert response.data['by_status']['DONE']['count'] == 3
        assert response.data['by_status']['IN_PROGRESS']['count'] == 1

    def test_filter_tasks_by_status(self, authenticated_client):
        """Test filtering tasks by status"""
        TaskFactory.create_batch(2, status='TODO')
        TaskFactory.create_batch(3, status='DONE')

        url = reverse('task-list') + '?status=DONE'

        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 3

    def test_search_tasks_by_title(self, authenticated_client):
        """Test searching tasks by title"""
        TaskFactory(title='Important Bug Fix')
        TaskFactory(title='Feature Request')
        TaskFactory(title='Another Bug')

        url = reverse('task-list') + '?search=Bug'

        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2


# ============================================================================
# USERSTORY VIEWSET TESTS
# ============================================================================

@pytest.mark.django_db
class TestUserStoryViewSet:
    """Test suite for UserStoryViewSet API endpoints"""

    def test_list_user_stories_requires_authentication(self, api_client):
        """Test listing user stories requires authentication"""
        url = reverse('userstory-list')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_user_stories_authenticated(self, authenticated_client):
        """Test authenticated user can list user stories"""
        UserStoryFactory.create_batch(3)
        url = reverse('userstory-list')

        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 3

    def test_create_user_story(self, authenticated_client):
        """Test creating a user story via API"""
        epic = EpicFactory()
        url = reverse('userstory-list')
        data = {
            'title': 'New User Story',
            'description': 'Story description',
            'epic': epic.id,
            'as_a': 'developer',
            'i_want': 'write tests',
            'so_that': 'code is reliable',
            'status': 'TODO',
            'priority': 'HIGH'
        }

        response = authenticated_client.post(url, data)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == 'New User Story'
        assert UserStory.objects.filter(title='New User Story').exists()

    def test_retrieve_user_story(self, authenticated_client):
        """Test retrieving a single user story"""
        story = UserStoryFactory(title='Test Story')
        url = reverse('userstory-detail', kwargs={'pk': story.id})

        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == 'Test Story'

    def test_update_user_story(self, authenticated_client):
        """Test updating a user story"""
        story = UserStoryFactory(status='TODO')
        url = reverse('userstory-detail', kwargs={'pk': story.id})
        data = {
            'title': story.title,
            'epic': story.epic.id,
            'status': 'DONE',
            'priority': story.priority
        }

        response = authenticated_client.patch(url, data)

        assert response.status_code == status.HTTP_200_OK
        story.refresh_from_db()
        assert story.status == 'DONE'

    def test_delete_user_story(self, authenticated_client):
        """Test deleting a user story"""
        story = UserStoryFactory()
        url = reverse('userstory-detail', kwargs={'pk': story.id})

        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not UserStory.objects.filter(id=story.id).exists()

    def test_user_story_tasks_endpoint(self, authenticated_client):
        """Test custom endpoint to get tasks for a user story"""
        story = UserStoryFactory()
        TaskFactory.create_batch(3, user_story=story)

        url = reverse('userstory-tasks', kwargs={'pk': story.id})

        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3

    def test_filter_user_stories_by_epic(self, authenticated_client):
        """Test filtering user stories by epic"""
        epic1 = EpicFactory()
        epic2 = EpicFactory()
        UserStoryFactory.create_batch(2, epic=epic1)
        UserStoryFactory.create_batch(3, epic=epic2)

        url = reverse('userstory-list') + f'?epic={epic2.id}'

        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 3


# ============================================================================
# EPIC VIEWSET TESTS
# ============================================================================

@pytest.mark.django_db
class TestEpicViewSet:
    """Test suite for EpicViewSet API endpoints"""

    def test_list_epics_requires_authentication(self, api_client):
        """Test listing epics requires authentication"""
        url = reverse('epic-list')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_epics_authenticated(self, authenticated_client):
        """Test authenticated user can list epics"""
        EpicFactory.create_batch(3)
        url = reverse('epic-list')

        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 3

    def test_create_epic(self, authenticated_client, user):
        """Test creating an epic via API"""
        url = reverse('epic-list')
        data = {
            'title': 'New Epic',
            'description': 'Epic description',
            'owner': user.id,
            'status': 'TODO',
            'priority': 'CRITICAL'
        }

        response = authenticated_client.post(url, data)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == 'New Epic'
        assert Epic.objects.filter(title='New Epic').exists()

    def test_retrieve_epic(self, authenticated_client):
        """Test retrieving a single epic"""
        epic = EpicFactory(title='Test Epic')
        url = reverse('epic-detail', kwargs={'pk': epic.id})

        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == 'Test Epic'

    def test_update_epic(self, authenticated_client):
        """Test updating an epic"""
        epic = EpicFactory(status='TODO')
        url = reverse('epic-detail', kwargs={'pk': epic.id})
        data = {
            'title': epic.title,
            'owner': epic.owner.id,
            'status': 'IN_PROGRESS',
            'priority': epic.priority
        }

        response = authenticated_client.patch(url, data)

        assert response.status_code == status.HTTP_200_OK
        epic.refresh_from_db()
        assert epic.status == 'IN_PROGRESS'

    def test_delete_epic(self, authenticated_client):
        """Test deleting an epic"""
        epic = EpicFactory()
        url = reverse('epic-detail', kwargs={'pk': epic.id})

        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Epic.objects.filter(id=epic.id).exists()

    def test_epic_user_stories_endpoint(self, authenticated_client):
        """Test custom endpoint to get user stories for an epic"""
        epic = EpicFactory()
        UserStoryFactory.create_batch(4, epic=epic)

        url = reverse('epic-user-stories', kwargs={'pk': epic.id})

        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 4

    def test_filter_epics_by_status(self, authenticated_client):
        """Test filtering epics by status"""
        EpicFactory.create_batch(2, status='TODO')
        EpicFactory.create_batch(3, status='IN_PROGRESS')

        url = reverse('epic-list') + '?status=IN_PROGRESS'

        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 3

    def test_search_epics_by_title(self, authenticated_client):
        """Test searching epics by title"""
        EpicFactory(title='Mobile App Development')
        EpicFactory(title='Backend API')
        EpicFactory(title='Mobile Testing')

        url = reverse('epic-list') + '?search=Mobile'

        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2