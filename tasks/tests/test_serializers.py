"""
Tests for tasks app serializers.

Tests for:
- TaskSerializer: validation, fields, nested serialization
- UserStorySerializer: validation, fields, nested serialization
- EpicSerializer: validation, fields, nested serialization
"""

import pytest
from rest_framework.exceptions import ValidationError as DRFValidationError

from tasks.serializers import TaskSerializer, UserStorySerializer, EpicSerializer
from tasks.tests.factories import UserFactory, EpicFactory, UserStoryFactory, TaskFactory


# ============================================================================
# TASK SERIALIZER TESTS
# ============================================================================

@pytest.mark.django_db
class TestTaskSerializer:
    """Test suite for TaskSerializer"""

    def test_serialize_task(self):
        """Test serializing a task"""
        task = TaskFactory()
        serializer = TaskSerializer(task)

        data = serializer.data

        assert data['id'] == task.id
        assert data['title'] == task.title
        assert data['status'] == task.status
        assert 'user_story' in data
        assert 'assigned_to_detail' in data

    def test_deserialize_valid_task_data(self):
        """Test deserializing valid task data"""
        user_story = UserStoryFactory()
        data = {
            'title': 'New Task',
            'description': 'Task description',
            'user_story': user_story.id,
            'status': 'TODO',
            'priority': 'HIGH'
        }

        serializer = TaskSerializer(data=data)

        assert serializer.is_valid()
        task = serializer.save()
        assert task.title == 'New Task'
        assert task.user_story == user_story

    def test_task_serializer_validation_reporter_equals_assigned_to(self):
        """Test validation fails when reporter equals assigned_to"""
        user = UserFactory()
        user_story = UserStoryFactory()
        data = {
            'title': 'Test Task',
            'user_story': user_story.id,
            'assigned_to': user.id,
            'reporter': user.id  # Same as assigned_to
        }

        serializer = TaskSerializer(data=data)

        assert not serializer.is_valid()
        assert 'reporter' in serializer.errors

    def test_task_serializer_allows_different_reporter_and_assigned_to(self):
        """Test validation passes with different reporter and assigned_to"""
        user1 = UserFactory()
        user2 = UserFactory()
        user_story = UserStoryFactory()
        data = {
            'title': 'Test Task',
            'user_story': user_story.id,
            'assigned_to': user1.id,
            'reporter': user2.id
        }

        serializer = TaskSerializer(data=data)

        assert serializer.is_valid()

    def test_task_serializer_read_only_fields(self):
        """Test read-only fields cannot be set"""
        task = TaskFactory()
        serializer = TaskSerializer(task)

        # These should be in read_only_fields
        assert 'created_at' in serializer.data
        assert 'updated_at' in serializer.data
        assert 'is_overdue' in serializer.data

    def test_task_serializer_includes_nested_user_details(self):
        """Test serializer includes nested user details"""
        user = UserFactory(username='testuser')
        task = TaskFactory(assigned_to=user)
        serializer = TaskSerializer(task)

        data = serializer.data

        assert 'assigned_to_detail' in data
        assert data['assigned_to_detail']['username'] == 'testuser'


# ============================================================================
# USERSTORY SERIALIZER TESTS
# ============================================================================

@pytest.mark.django_db
class TestUserStorySerializer:
    """Test suite for UserStorySerializer"""

    def test_serialize_user_story(self):
        """Test serializing a user story"""
        story = UserStoryFactory()
        serializer = UserStorySerializer(story)

        data = serializer.data

        assert data['id'] == story.id
        assert data['title'] == story.title
        assert 'epic' in data
        assert 'tasks_count' in data
        assert 'completion_percentage' in data

    def test_deserialize_valid_user_story_data(self):
        """Test deserializing valid user story data"""
        epic = EpicFactory()
        data = {
            'title': 'New Story',
            'description': 'Story description',
            'epic': epic.id,
            'as_a': 'user',
            'i_want': 'do something',
            'so_that': 'achieve goal',
            'status': 'TODO',
            'priority': 'MEDIUM'
        }

        serializer = UserStorySerializer(data=data)

        assert serializer.is_valid()
        story = serializer.save()
        assert story.title == 'New Story'
        assert story.epic == epic

    def test_user_story_serializer_validation_reporter_equals_assigned_to(self):
        """Test validation fails when reporter equals assigned_to"""
        user = UserFactory()
        epic = EpicFactory()
        data = {
            'title': 'Test Story',
            'epic': epic.id,
            'assigned_to': user.id,
            'reporter': user.id
        }

        serializer = UserStorySerializer(data=data)

        assert not serializer.is_valid()
        assert 'reporter' in serializer.errors

    def test_user_story_serializer_computed_fields(self):
        """Test serializer includes computed fields"""
        story = UserStoryFactory()
        # Create some tasks for the story
        TaskFactory.create_batch(2, user_story=story, status='DONE')
        TaskFactory(user_story=story, status='TODO')

        serializer = UserStorySerializer(story)
        data = serializer.data

        assert data['tasks_count'] == 3
        # 2 out of 3 done = 66.67%
        assert abs(data['completion_percentage'] - 66.67) < 0.1

    def test_user_story_serializer_includes_tasks(self):
        """Test serializer includes nested tasks"""
        story = UserStoryFactory()
        TaskFactory.create_batch(2, user_story=story)

        serializer = UserStorySerializer(story)
        data = serializer.data

        assert 'tasks' in data
        assert len(data['tasks']) == 2


# ============================================================================
# EPIC SERIALIZER TESTS
# ============================================================================

@pytest.mark.django_db
class TestEpicSerializer:
    """Test suite for EpicSerializer"""

    def test_serialize_epic(self):
        """Test serializing an epic"""
        epic = EpicFactory()
        serializer = EpicSerializer(epic)

        data = serializer.data

        assert data['id'] == epic.id
        assert data['title'] == epic.title
        assert 'owner' in data
        assert 'user_stories_count' in data
        assert 'completion_percentage' in data

    def test_deserialize_valid_epic_data(self):
        """Test deserializing valid epic data"""
        owner = UserFactory()
        data = {
            'title': 'New Epic',
            'description': 'Epic description',
            'owner': owner.id,
            'status': 'TODO',
            'priority': 'HIGH'
        }

        serializer = EpicSerializer(data=data)

        assert serializer.is_valid()
        epic = serializer.save()
        assert epic.title == 'New Epic'
        assert epic.owner == owner

    def test_epic_serializer_computed_fields(self):
        """Test serializer includes computed fields"""
        epic = EpicFactory()
        # Create user stories
        UserStoryFactory.create_batch(3, epic=epic, status='DONE')
        UserStoryFactory(epic=epic, status='TODO')

        serializer = EpicSerializer(epic)
        data = serializer.data

        assert data['user_stories_count'] == 4
        # 3 out of 4 done = 75%
        assert data['completion_percentage'] == 75.0

    def test_epic_serializer_includes_user_stories(self):
        """Test serializer includes nested user stories"""
        epic = EpicFactory()
        UserStoryFactory.create_batch(3, epic=epic)

        serializer = EpicSerializer(epic)
        data = serializer.data

        assert 'user_stories' in data
        assert len(data['user_stories']) == 3

    def test_epic_serializer_includes_owner_detail(self):
        """Test serializer includes owner details"""
        owner = UserFactory(username='epicowner')
        epic = EpicFactory(owner=owner)

        serializer = EpicSerializer(epic)
        data = serializer.data

        assert 'owner_detail' in data
        assert data['owner_detail']['username'] == 'epicowner'