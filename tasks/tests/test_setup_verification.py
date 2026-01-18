"""
Test file to verify your testing infrastructure is working correctly.

Run this first before writing actual tests:
    pytest tasks/tests/test_setup_verification.py -v

If all pass, your setup is correct!
"""

import pytest
from django.contrib.auth import get_user_model
# from .tasks.tests.factories import UserFactory, EpicFactory, UserStoryFactory, TaskFactory
from tasks.models import Epic, UserStory, Task
from tasks.tests.factories import UserFactory, TaskFactory, UserStoryFactory, EpicFactory

User = get_user_model()


def test_user_fixture_exists(user):
    """Verify the user fixture works"""
    assert user is not None
    assert user.username == 'testuser'
    assert user.email == 'test@example.com'
    assert user.check_password('testpass123')  # Password is hashed


def test_users_fixture_exists(users):
    """Verify the users fixture creates multiple users"""
    assert len(users) == 3
    assert 'user1' in users
    assert 'user2' in users
    assert 'user3' in users
    assert users['user1'].username == 'user1'


def test_api_client_fixture_exists(api_client):
    """Verify API client fixture works"""
    assert api_client is not None
    # Should be able to make requests
    response = api_client.get('/api/tasks/')
    # Might be 401 (unauthorized) or 403 (forbidden), but not 404
    assert response.status_code in [401, 403, 200]


def test_authenticated_client_fixture(authenticated_client):
    """Verify authenticated client has user"""
    # Client should have a user attached
    assert authenticated_client.handler._force_user is not None


@pytest.mark.django_db
def test_user_factory_creates_user():
    """Test UserFactory creates a valid user"""
    user = UserFactory()

    assert user.id is not None  # Saved to database
    assert user.username.startswith('user')
    assert '@example.com' in user.email
    assert user.check_password('testpass123')  # Password properly hashed


@pytest.mark.django_db
def test_user_factory_creates_unique_users():
    """Test UserFactory creates unique users"""
    user1 = UserFactory()
    user2 = UserFactory()

    assert user1.username != user2.username
    assert user1.email != user2.email


@pytest.mark.django_db
def test_epic_factory_creates_epic():
    """Test EpicFactory creates valid epic with owner"""
    epic = EpicFactory()

    assert epic.id is not None
    assert epic.title.startswith('Epic')
    assert epic.owner is not None  # SubFactory created owner
    assert isinstance(epic.owner, User)
    assert epic.status == 'TODO'


@pytest.mark.django_db
def test_user_story_factory_creates_user_story():
    """Test UserStoryFactory creates valid user story"""
    story = UserStoryFactory()

    assert story.id is not None
    assert story.title.startswith('User Story')
    assert story.epic is not None  # SubFactory created epic
    assert story.epic.owner is not None  # Epic has owner
    assert story.assigned_to is not None
    assert story.reporter is not None
    # Validation: reporter != assigned_to
    assert story.reporter != story.assigned_to


@pytest.mark.django_db
def test_task_factory_creates_task():
    """Test TaskFactory creates valid task with full hierarchy"""
    task = TaskFactory()

    assert task.id is not None
    assert task.title.startswith('Task')
    assert task.user_story is not None
    assert task.user_story.epic is not None
    assert task.user_story.epic.owner is not None
    assert task.assigned_to is not None
    assert task.reporter is not None
    # Validation: reporter != assigned_to
    assert task.reporter != task.assigned_to


@pytest.mark.django_db
def test_factory_can_override_fields():
    """Test factories allow field overrides"""
    custom_title = 'My Custom Task'
    task = TaskFactory(title=custom_title, status='DONE')

    assert task.title == custom_title
    assert task.status == 'DONE'


@pytest.mark.django_db
def test_factory_create_batch():
    """Test factories can create multiple instances"""
    tasks = TaskFactory.create_batch(5)

    assert len(tasks) == 5
    assert all(isinstance(task, Task) for task in tasks)
    # Each should have unique title
    titles = [task.title for task in tasks]
    assert len(set(titles)) == 5  # All unique


@pytest.mark.django_db
def test_database_access_works():
    """Verify we can query the database"""
    # Create some data
    UserFactory.create_batch(3)

    # Query it
    count = User.objects.count()
    assert count >= 3


@pytest.mark.django_db
def test_database_isolation():
    """Verify each test gets clean database"""
    # This test should start with no users (except fixtures)
    initial_count = User.objects.count()
    # Create a user
    UserFactory()
    # Count increased
    assert User.objects.count() == initial_count + 1
    # Note: After this test, database rolls back
    # Next test won't see this user


@pytest.mark.django_db
def test_epic_to_user_stories_relationship():
    """Test Epic -> UserStory relationship"""
    epic = EpicFactory()
    story1 = UserStoryFactory(epic=epic)
    story2 = UserStoryFactory(epic=epic)

    # Epic should have 2 user stories
    assert epic.user_stories.count() == 2
    assert story1 in epic.user_stories.all()
    assert story2 in epic.user_stories.all()


@pytest.mark.django_db
def test_user_story_to_tasks_relationship():
    """Test UserStory -> Task relationship"""
    story = UserStoryFactory()
    task1 = TaskFactory(user_story=story)
    task2 = TaskFactory(user_story=story)

    # Story should have 2 tasks
    assert story.tasks.count() == 2
    assert task1 in story.tasks.all()
    assert task2 in story.tasks.all()
