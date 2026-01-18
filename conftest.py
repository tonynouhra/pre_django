"""
Global pytest fixtures shared across all test modules.

Fixtures are reusable test setup functions. They:
- Run before each test that uses them
- Provide test data (users, clients, etc.)
- Clean up automatically after tests
"""
import os
import django

# Configure Django settings BEFORE any Django imports
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taskmanager.settings')
django.setup()

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    """
    Configure test database to use faster password hashing.

    Why: Django's default password hasher (bcrypt/pbkdf2) is intentionally
    slow for security. For tests, we use MD5 for 10x faster user creation.

    Scope='session': Runs once per entire test session
    """
    settings.PASSWORD_HASHERS = [
        'django.contrib.auth.hashers.MD5PasswordHasher',
    ]


@pytest.fixture
def api_client():
    """
    Provides DRF's APIClient for making HTTP requests in tests.

    Usage in tests:
        def test_something(api_client):
            response = api_client.get('/api/tasks/')
            assert response.status_code == 200

    Returns:
        APIClient: REST framework test client
    """
    return APIClient()


@pytest.fixture
def user(db):
    """
    Creates a basic test user.

    Why 'db' parameter: Tells pytest this fixture needs database access.
    Without it, you'll get "no database access" errors.

    Usage:
        def test_user_has_email(user):
            assert '@' in user.email

    Returns:
        User: A user with username='testuser', password='testpass123'
    """
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User'
    )


@pytest.fixture
def users(db):
    """
    Creates multiple test users for testing relationships and assignments.

    Use when you need different users for:
    - owner vs reporter
    - assigned_to vs creator
    - Testing permissions

    Usage:
        def test_assignment(users):
            epic = Epic.objects.create(
                title='Epic 1',
                owner=users['user1'],
                reporter=users['user2']
            )

    Returns:
        dict: {'user1': User, 'user2': User, 'user3': User}
    """
    user1 = User.objects.create_user(
        username='user1',
        email='user1@example.com',
        password='testpass123'
    )
    user2 = User.objects.create_user(
        username='user2',
        email='user2@example.com',
        password='testpass123'
    )
    user3 = User.objects.create_user(
        username='user3',
        email='user3@example.com',
        password='testpass123'
    )
    return {
        'user1': user1,
        'user2': user2,
        'user3': user3,
    }


@pytest.fixture
def authenticated_client(api_client, user):
    """
    Provides an API client that's already logged in with JWT token.

    Why: Most of your API endpoints require authentication.
    This saves you from manually authenticating in every test.

    Usage:
        def test_protected_endpoint(authenticated_client):
            response = authenticated_client.get('/api/tasks/')
            # No need to set auth headers manually!
            assert response.status_code == 200

    Alternative methods:
    1. Force authenticate (what we use - simple, fast)
    2. Get JWT token and set header (more realistic but slower)

    Returns:
        APIClient: Authenticated client ready to make requests
    """
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def authenticated_client_with_token(api_client, user):
    """
    Alternative: Client with actual JWT token (more realistic).

    Use this when you need to test JWT token behavior specifically.
    For most tests, use 'authenticated_client' instead (faster).

    Usage:
        def test_token_in_header(authenticated_client_with_token):
            response = authenticated_client_with_token.get('/api/tasks/')
            assert response.status_code == 200
    """

    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)

    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    return api_client
