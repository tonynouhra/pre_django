"""
Unit tests for accounts app models.

This file will contain tests for:
- CustomUser model creation
- User authentication
- User relationships (epics, stories, tasks)
"""

import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


# Tests will be added here
# Example placeholder:
@pytest.mark.django_db
def test_user_creation():
    """Test basic user creation"""
    user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )
    assert user.username == 'testuser'
    assert user.email == 'test@example.com'
    assert user.check_password('testpass123')