"""
Unit tests for tasks app models.

Tests for:
- Task model: creation, validation, properties, relationships
- UserStory model: creation, validation, properties, relationships
- Epic model: creation, validation, properties, relationships
"""

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model

from tasks.models import Epic, UserStory, Task
from tasks.tests.factories import UserFactory, EpicFactory, UserStoryFactory, TaskFactory

User = get_user_model()


# ============================================================================
# TASK MODEL TESTS
# ============================================================================

@pytest.mark.django_db
class TestTaskModel:
    """Test suite for Task model"""

    def test_task_creation_with_required_fields(self):
        """Test creating a task with all required fields"""
        task = TaskFactory()

        assert task.id is not None
        assert task.title is not None
        assert task.user_story is not None
        assert task.status == 'TODO'
        assert task.priority == 'MEDIUM'

    def test_task_default_values(self):
        """Test task default values are set correctly"""
        user_story = UserStoryFactory()
        task = Task.objects.create(
            title='Test Task',
            user_story=user_story
        )

        assert task.status == 'TODO'
        assert task.priority == 'MEDIUM'
        assert task.actual_hours is None
        assert task.completed_at is None

    def test_task_string_representation(self):
        """Test __str__ returns 'title - user_story.title'"""
        task = TaskFactory(title='My Task')
        expected = f"{task.title} - {task.user_story.title}"

        assert str(task) == expected

    def test_task_assigned_to_relationship(self):
        """Test task can be assigned to a user"""
        user = UserFactory()
        task = TaskFactory(assigned_to=user)

        assert task.assigned_to == user
        assert task in user.assigned_tasks.all()

    def test_task_reporter_relationship(self):
        """Test task has reporter relationship"""
        reporter = UserFactory()
        task = TaskFactory(reporter=reporter)

        assert task.reporter == reporter
        assert task in reporter.reported_tasks.all()

    def test_task_belongs_to_user_story(self):
        """Test task belongs to a user story"""
        story = UserStoryFactory()
        task = TaskFactory(user_story=story)

        assert task.user_story == story
        assert task in story.tasks.all()

    def test_task_is_overdue_when_past_due_date(self):
        """Test is_overdue returns True when due_date is in the past"""
        past_date = timezone.now() - timedelta(days=5)
        task = TaskFactory(
            due_date=past_date,
            status='IN_PROGRESS'
        )

        assert task.is_overdue is True

    def test_task_is_not_overdue_when_future_due_date(self):
        """Test is_overdue returns False when due_date is in the future"""
        future_date = timezone.now() + timedelta(days=5)
        task = TaskFactory(due_date=future_date)

        assert task.is_overdue is False

    def test_task_is_not_overdue_when_done(self):
        """Test is_overdue returns False when task is done"""
        past_date = timezone.now() - timedelta(days=5)
        task = TaskFactory(
            due_date=past_date,
            status='DONE'
        )

        assert task.is_overdue is False

    def test_task_is_not_overdue_when_no_due_date(self):
        """Test is_overdue returns False when no due_date set"""
        task = TaskFactory(due_date=None)

        assert task.is_overdue is False

    def test_task_validation_reporter_cannot_equal_assigned_to(self):
        """Test validation: reporter cannot be same as assigned_to"""
        user = UserFactory()
        task = Task(
            title='Test Task',
            user_story=UserStoryFactory(),
            assigned_to=user,
            reporter=user
        )

        with pytest.raises(ValidationError) as exc_info:
            task.clean()

        assert 'reporter' in exc_info.value.message_dict
        assert 'cannot be the same' in str(exc_info.value.message_dict['reporter'][0]).lower()

    def test_task_can_have_different_reporter_and_assigned_to(self):
        """Test task can have different reporter and assigned_to"""
        user1 = UserFactory()
        user2 = UserFactory()
        task = Task(
            title='Test Task',
            user_story=UserStoryFactory(),
            assigned_to=user1,
            reporter=user2
        )

        # Should not raise ValidationError
        task.clean()
        task.save()
        assert task.assigned_to != task.reporter


# ============================================================================
# USERSTORY MODEL TESTS
# ============================================================================

@pytest.mark.django_db
class TestUserStoryModel:
    """Test suite for UserStory model"""

    def test_user_story_creation_with_required_fields(self):
        """Test creating a user story with required fields"""
        story = UserStoryFactory()

        assert story.id is not None
        assert story.title is not None
        assert story.epic is not None

    def test_user_story_default_values(self):
        """Test user story default values"""
        epic = EpicFactory()
        story = UserStory.objects.create(
            title='Test Story',
            epic=epic
        )

        assert story.status == 'TODO'
        assert story.priority == 'MEDIUM'

    def test_user_story_string_representation(self):
        """Test __str__ returns 'title - epic.title'"""
        story = UserStoryFactory(title='My Story')
        expected = f"{story.title} - {story.epic.title}"

        assert str(story) == expected

    def test_user_story_belongs_to_epic(self):
        """Test user story belongs to an epic"""
        epic = EpicFactory()
        story = UserStoryFactory(epic=epic)

        assert story.epic == epic
        assert story in epic.user_stories.all()

    def test_user_story_tasks_count_property(self):
        """Test tasks_count property returns correct count"""
        story = UserStoryFactory()

        # Initially 0 tasks
        assert story.tasks_count == 0

        # Create 3 tasks
        TaskFactory.create_batch(3, user_story=story)

        assert story.tasks_count == 3

    def test_user_story_completion_percentage_with_no_tasks(self):
        """Test completion_percentage returns 0 when no tasks"""
        story = UserStoryFactory()

        assert story.completion_percentage == 0

    def test_user_story_completion_percentage_with_no_done_tasks(self):
        """Test completion_percentage returns 0 when no tasks are done"""
        story = UserStoryFactory()
        TaskFactory.create_batch(3, user_story=story, status='TODO')

        assert story.completion_percentage == 0

    def test_user_story_completion_percentage_with_some_done_tasks(self):
        """Test completion_percentage calculates correctly"""
        story = UserStoryFactory()

        # Create 4 tasks: 2 done, 2 not done
        TaskFactory.create_batch(2, user_story=story, status='DONE')
        TaskFactory.create_batch(2, user_story=story, status='TODO')

        assert story.completion_percentage == 50.0

    def test_user_story_completion_percentage_all_done(self):
        """Test completion_percentage returns 100 when all tasks done"""
        story = UserStoryFactory()
        TaskFactory.create_batch(3, user_story=story, status='DONE')

        assert story.completion_percentage == 100.0

    def test_user_story_full_story_property_with_agile_fields(self):
        """Test full_story returns formatted agile story"""
        story = UserStoryFactory(
            as_a='developer',
            i_want='write tests',
            so_that='code is reliable'
        )

        expected = "As a developer, I want write tests, so that code is reliable"
        assert story.full_story == expected

    def test_user_story_full_story_property_without_agile_fields(self):
        """Test full_story returns description when agile fields empty"""
        story = UserStoryFactory(
            as_a='',
            i_want='',
            so_that='',
            description='Just a regular description'
        )

        assert story.full_story == 'Just a regular description'

    def test_user_story_validation_reporter_cannot_equal_assigned_to(self):
        """Test validation: reporter cannot be same as assigned_to"""
        user = UserFactory()
        story = UserStory(
            title='Test Story',
            epic=EpicFactory(),
            assigned_to=user,
            reporter=user
        )

        with pytest.raises(ValidationError) as exc_info:
            story.clean()

        assert 'reporter' in exc_info.value.message_dict


# ============================================================================
# EPIC MODEL TESTS
# ============================================================================

@pytest.mark.django_db
class TestEpicModel:
    """Test suite for Epic model"""

    def test_epic_creation_with_required_fields(self):
        """Test creating an epic with required fields"""
        epic = EpicFactory()

        assert epic.id is not None
        assert epic.title is not None
        assert epic.owner is not None

    def test_epic_default_values(self):
        """Test epic default values"""
        user = UserFactory()
        epic = Epic.objects.create(
            title='Test Epic',
            owner=user
        )

        assert epic.status == 'TODO'
        assert epic.priority == 'MEDIUM'

    def test_epic_string_representation(self):
        """Test __str__ returns 'title (status)'"""
        epic = EpicFactory(title='My Epic', status='IN_PROGRESS')
        expected = "My Epic (IN_PROGRESS)"

        assert str(epic) == expected

    def test_epic_owner_relationship(self):
        """Test epic has owner relationship"""
        owner = UserFactory()
        epic = EpicFactory(owner=owner)

        assert epic.owner == owner
        assert epic in owner.epics.all()

    def test_epic_reporter_relationship(self):
        """Test epic has optional reporter relationship"""
        reporter = UserFactory()
        epic = EpicFactory(reporter=reporter)

        assert epic.reporter == reporter
        assert epic in reporter.reported_epics.all()

    def test_epic_user_stories_count_property(self):
        """Test user_stories_count property returns correct count"""
        epic = EpicFactory()

        # Initially 0 user stories
        assert epic.user_stories_count == 0

        # Create 5 user stories
        UserStoryFactory.create_batch(5, epic=epic)

        assert epic.user_stories_count == 5

    def test_epic_completion_percentage_with_no_user_stories(self):
        """Test completion_percentage returns 0 when no user stories"""
        epic = EpicFactory()

        assert epic.completion_percentage == 0

    def test_epic_completion_percentage_with_no_done_stories(self):
        """Test completion_percentage returns 0 when no stories are done"""
        epic = EpicFactory()
        UserStoryFactory.create_batch(3, epic=epic, status='TODO')

        assert epic.completion_percentage == 0

    def test_epic_completion_percentage_with_some_done_stories(self):
        """Test completion_percentage calculates correctly"""
        epic = EpicFactory()

        # Create 4 stories: 1 done, 3 not done
        UserStoryFactory(epic=epic, status='DONE')
        UserStoryFactory.create_batch(3, epic=epic, status='TODO')

        assert epic.completion_percentage == 25.0

    def test_epic_completion_percentage_all_done(self):
        """Test completion_percentage returns 100 when all stories done"""
        epic = EpicFactory()
        UserStoryFactory.create_batch(3, epic=epic, status='DONE')

        assert epic.completion_percentage == 100.0

    def test_epic_can_have_multiple_user_stories(self):
        """Test epic can have multiple user stories"""
        epic = EpicFactory()
        stories = UserStoryFactory.create_batch(3, epic=epic)

        assert epic.user_stories.count() == 3
        for story in stories:
            assert story in epic.user_stories.all()