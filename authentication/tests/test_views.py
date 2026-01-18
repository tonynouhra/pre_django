"""
API tests for authentication endpoints.

Tests for:
- User registration (POST /api/auth/register/)
- JWT token generation (POST /api/auth/login/)
- Token refresh (POST /api/auth/token/refresh/)
- User profile retrieval (GET /api/auth/profile/)
- User profile update (PUT/PATCH /api/auth/profile/)
"""

import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from tasks.tests.factories import UserFactory

User = get_user_model()


# ============================================================================
# USER REGISTRATION TESTS
# ============================================================================

@pytest.mark.django_db
class TestUserRegistration:
    """Test suite for user registration endpoint"""

    def test_register_user_with_valid_data(self, api_client):
        """Test user registration with valid data"""
        url = reverse('register')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'StrongPass123!',
            'password2': 'StrongPass123!',
            'first_name': 'New',
            'last_name': 'User'
        }

        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_201_CREATED
        assert 'user' in response.data
        assert response.data['user']['username'] == 'newuser'
        assert User.objects.filter(username='newuser').exists()

    def test_register_user_passwords_dont_match(self, api_client):
        """Test registration fails when passwords don't match"""
        url = reverse('register')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'StrongPass123!',
            'password2': 'DifferentPass123!',
        }

        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password' in response.data or 'non_field_errors' in response.data

    def test_register_user_with_weak_password(self, api_client):
        """Test registration fails with weak password"""
        url = reverse('register')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': '123',  # Too weak
            'password2': '123',
        }

        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_user_duplicate_username(self, api_client):
        """Test registration fails with duplicate username"""
        UserFactory(username='existinguser')

        url = reverse('register')
        data = {
            'username': 'existinguser',  # Already exists
            'email': 'new@example.com',
            'password': 'StrongPass123!',
            'password2': 'StrongPass123!',
        }

        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_user_duplicate_email(self, api_client):
        """Test registration fails with duplicate email"""
        UserFactory(email='existing@example.com')

        url = reverse('register')
        data = {
            'username': 'newuser',
            'email': 'existing@example.com',  # Already exists
            'password': 'StrongPass123!',
            'password2': 'StrongPass123!',
        }

        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_user_missing_required_fields(self, api_client):
        """Test registration fails with missing required fields"""
        url = reverse('register')
        data = {
            'username': 'newuser',
            # Missing email and passwords
        }

        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST


# ============================================================================
# JWT TOKEN AUTHENTICATION TESTS
# ============================================================================

@pytest.mark.django_db
class TestJWTAuthentication:
    """Test suite for JWT token authentication"""

    def test_obtain_token_with_valid_credentials(self, api_client):
        """Test obtaining JWT token with valid credentials"""
        user = UserFactory(username='testuser')
        user.set_password('testpass123')
        user.save()

        url = reverse('login')
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }

        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data

    def test_obtain_token_with_invalid_credentials(self, api_client):
        """Test token generation fails with invalid credentials"""
        UserFactory(username='testuser', password='correctpass')

        url = reverse('login')
        data = {
            'username': 'testuser',
            'password': 'wrongpass'
        }

        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_obtain_token_with_nonexistent_user(self, api_client):
        """Test token generation fails with non-existent user"""
        url = reverse('login')
        data = {
            'username': 'nonexistent',
            'password': 'somepass'
        }

        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_refresh_token_with_valid_refresh(self, api_client):
        """Test refreshing access token with valid refresh token"""
        user = UserFactory()
        refresh = RefreshToken.for_user(user)

        url = reverse('token_refresh')
        data = {
            'refresh': str(refresh)
        }

        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data

    def test_refresh_token_with_invalid_refresh(self, api_client):
        """Test refresh fails with invalid refresh token"""
        url = reverse('token_refresh')
        data = {
            'refresh': 'invalid_token'
        }

        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ============================================================================
# USER PROFILE TESTS
# ============================================================================

@pytest.mark.django_db
class TestUserProfile:
    """Test suite for user profile endpoints"""

    def test_get_profile_authenticated(self, authenticated_client, user):
        """Test authenticated user can retrieve their profile"""
        url = reverse('profile')

        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == user.username
        assert response.data['email'] == user.email

    def test_get_profile_unauthenticated(self, api_client):
        """Test unauthenticated user cannot access profile"""
        url = reverse('profile')

        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_profile_authenticated(self, authenticated_client, user):
        """Test authenticated user can update their profile"""
        url = reverse('profile')
        data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'bio': 'Updated bio'
        }

        response = authenticated_client.patch(url, data)

        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.first_name == 'Updated'
        assert user.last_name == 'Name'

    def test_update_profile_cannot_change_username(self, authenticated_client, user):
        """Test user cannot change their username via profile update"""
        url = reverse('profile')
        original_username = user.username
        data = {
            'username': 'newusername'  # Should be read-only
        }

        response = authenticated_client.patch(url, data)

        user.refresh_from_db()
        # Username should remain unchanged
        assert user.username == original_username

    def test_update_profile_unauthenticated(self, api_client):
        """Test unauthenticated user cannot update profile"""
        url = reverse('profile')
        data = {
            'first_name': 'Updated'
        }

        response = api_client.patch(url, data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ============================================================================
# AUTHENTICATION FLOW TESTS
# ============================================================================

@pytest.mark.django_db
class TestAuthenticationFlow:
    """Test complete authentication workflows"""

    def test_complete_registration_and_login_flow(self, api_client):
        """Test complete flow: register -> login -> get token -> access protected resource"""
        # Step 1: Register
        register_url = reverse('register')
        register_data = {
            'username': 'flowuser',
            'email': 'flowuser@example.com',
            'password': 'StrongPass123!',
            'password2': 'StrongPass123!',
        }
        register_response = api_client.post(register_url, register_data)
        assert register_response.status_code == status.HTTP_201_CREATED

        # Step 2: Login to get token
        login_url = reverse('login')
        login_data = {
            'username': 'flowuser',
            'password': 'StrongPass123!'
        }
        login_response = api_client.post(login_url, login_data)
        assert login_response.status_code == status.HTTP_200_OK
        token = login_response.data['access']

        # Step 3: Access protected resource with token
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        profile_url = reverse('profile')
        profile_response = api_client.get(profile_url)

        assert profile_response.status_code == status.HTTP_200_OK
        assert profile_response.data['username'] == 'flowuser'

    def test_token_refresh_flow(self, api_client):
        """Test flow: login -> use refresh token -> get new access token"""
        # Create user and login
        user = UserFactory(username='refreshuser')
        user.set_password('testpass123')
        user.save()

        login_url = reverse('login')
        login_data = {
            'username': 'refreshuser',
            'password': 'testpass123'
        }
        login_response = api_client.post(login_url, login_data)
        refresh_token = login_response.data['refresh']

        # Use refresh token to get new access token
        refresh_url = reverse('token_refresh')
        refresh_data = {
            'refresh': refresh_token
        }
        refresh_response = api_client.post(refresh_url, refresh_data)

        assert refresh_response.status_code == status.HTTP_200_OK
        assert 'access' in refresh_response.data

        # Use new access token to access protected resource
        new_access_token = refresh_response.data['access']
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {new_access_token}')
        profile_url = reverse('profile')
        profile_response = api_client.get(profile_url)

        assert profile_response.status_code == status.HTTP_200_OK