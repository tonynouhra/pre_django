"""
  Factory Boy factories for generating test data.

  Why use factories instead of manual object creation?
  1. Less code repetition
  2. Realistic fake data (using Faker)
  3. Automatic handling of relationships
  4. Easy to override specific fields
  5. Can create batches: TaskFactory.create_batch(10)

  Basic usage:
      task = TaskFactory()  # Creates Task + UserStory + Epic + Users
      task = TaskFactory(title='My Task')  # Override specific field
      tasks = TaskFactory.create_batch(5)  # Create 5 tasks
  """
import factory
from factory.django import DjangoModelFactory
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from tasks.models import Epic, UserStory, Task

User = get_user_model()


class UserFactory(DjangoModelFactory):
    """
    Factory for creating test users.

    Generates:
    - Unique usernames (user1, user2, user3...)
    - Unique emails (user1@example.com, ...)
    - Realistic names (from Faker)
    - Properly hashed passwords

    Usage:
        user = UserFactory()
        user = UserFactory(username='custom_name')
        users = UserFactory.create_batch(3)
    """

    class Meta:
        model = User

    # Sequence: Generates unique values by appending a counter

    # lambda n: n is 1, 2, 3... for each instance
    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.Sequence(lambda n: f'user{n}@example.com')

    # Faker: Generates realistic fake data
    # See: https://faker.readthedocs.io/en/master/providers.html
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')

    # PostGenerationMethodCall: Calls model method after creation
    # This properly hashes the password instead of storing it plain
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')


class EpicFactory(DjangoModelFactory):
    """
    Factory for creating test epics.

    Automatically creates:
    - owner (via SubFactory -> creates a User)
    - Optional reporter (via SubFactory)

    Usage:
        epic = EpicFactory()
        epic = EpicFactory(title='My Epic', status='IN_PROGRESS')
        epic = EpicFactory(owner=my_existing_user)  # Use existing user
    """

    class Meta:
        model = Epic

    title = factory.Sequence(lambda n: f'Epic {n}')
    description = factory.Faker('text', max_nb_chars=200)

    # Choices from your model
    status = 'TODO'
    priority = 'MEDIUM'

    # SubFactory: Automatically creates related object
    # If you pass owner=some_user, it won't create new user
    owner = factory.SubFactory(UserFactory)

    # reporter can be None (nullable in model)
    reporter = None

    # LazyFunction: Generates value when factory is called (not when defined)
    # Today's date
    start_date = factory.LazyFunction(lambda: timezone.now().date())

    # 30 days from now
    due_date = factory.LazyFunction(
        lambda: (timezone.now() + timedelta(days=30)).date()
    )


class UserStoryFactory(DjangoModelFactory):
    """
    Factory for creating test user stories.

    Automatically creates:
    - epic (which creates owner User)
    - assigned_to User
    - reporter User

    Usage:
        story = UserStoryFactory()
        story = UserStoryFactory(status='DONE', story_points=8)

        # Nested SubFactory syntax: Set epic's owner
        story = UserStoryFactory(epic__owner=my_user)
        story = UserStoryFactory(epic__title='My Epic')
    """

    class Meta:
        model = UserStory

    title = factory.Sequence(lambda n: f'User Story {n}')
    description = factory.Faker('paragraph', nb_sentences=3)

    # Agile user story format fields
    as_a = 'user'
    i_want = factory.Faker('sentence', nb_words=6)
    so_that = factory.Faker('sentence', nb_words=6)

    status = 'TODO'
    priority = 'MEDIUM'

    # SubFactory creates Epic, which creates owner User
    epic = factory.SubFactory(EpicFactory)

    # Create separate users for assigned_to and reporter
    # This avoids validation error (they can't be same user)
    assigned_to = factory.SubFactory(UserFactory)
    reporter = factory.SubFactory(UserFactory)

    # Story points (Fibonacci sequence)
    story_points = 5

    start_date = factory.LazyFunction(lambda: timezone.now().date())
    due_date = factory.LazyFunction(
        lambda: (timezone.now() + timedelta(days=14)).date()
    )


class TaskFactory(DjangoModelFactory):
    """
    Factory for creating test tasks.

    Automatically creates entire hierarchy:
    Task -> UserStory -> Epic -> Users

    Usage:
        task = TaskFactory()
        task = TaskFactory(status='DONE', estimated_hours=16)

        # Use existing user_story
        task = TaskFactory(user_story=my_story)

        # Override nested epic title
        task = TaskFactory(user_story__epic__title='My Epic')

        # Create overdue task
        overdue_task = TaskFactory(
            due_date=timezone.now() - timedelta(days=5),
            status='IN_PROGRESS'
        )
    """

    class Meta:
        model = Task

    title = factory.Sequence(lambda n: f'Task {n}')
    description = factory.Faker('text', max_nb_chars=300)

    status = 'TODO'
    priority = 'MEDIUM'

    # Creates UserStory -> Epic -> Users
    user_story = factory.SubFactory(UserStoryFactory)

    # Create separate users for assigned_to and reporter
    assigned_to = factory.SubFactory(UserFactory)
    reporter = factory.SubFactory(UserFactory)

    # Estimation fields
    estimated_hours = 8.0
    actual_hours = None  # Not completed yet

    # Due date 7 days from now (not overdue)
    due_date = factory.LazyFunction(
        lambda: timezone.now() + timedelta(days=7)
    )

    completed_at = None  # Not completed
