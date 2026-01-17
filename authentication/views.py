from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model

from .serializers import UserRegistrationSerializer, UserSerializer

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """
    User registration endpoint
    POST /api/auth/register/
    """
    queryset = User.objects.all()
    permission_classes = [
        AllowAny]  # Anyone can register
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response({
            'user': UserSerializer(user).data,
            'message': 'User created successfully. Please login to get your token.'
        }, status=status.HTTP_201_CREATED)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Get or update current user profile
    GET/PUT /api/auth/profile/
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user