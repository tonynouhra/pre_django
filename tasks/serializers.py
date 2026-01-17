from rest_framework import serializers
from .models import Epic, UserStory, Task
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model (simplified)"""

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class TaskSerializer(serializers.ModelSerializer):
    """Serializer for Task model"""

    # Show assigned user details (read-only)
    assigned_to_detail = UserSerializer(source='assigned_to', read_only=True)

    # Show computed properties
    is_overdue = serializers.ReadOnlyField()

    class Meta:
        model = Task
        fields = [
            'id',
            'title',
            'description',
            'status',
            'priority',
            'user_story',
            'assigned_to',
            'assigned_to_detail',
            'estimated_hours',
            'actual_hours',
            'due_date',
            'completed_at',
            'is_overdue',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_overdue']


class UserStorySerializer(serializers.ModelSerializer):
    """Serializer for UserStory model"""

    # Nested tasks (read-only)
    tasks = TaskSerializer(many=True, read_only=True)

    # Show assigned user details
    assigned_to_detail = UserSerializer(source='assigned_to', read_only=True)

    # Show computed properties
    tasks_count = serializers.ReadOnlyField()
    completion_percentage = serializers.ReadOnlyField()
    full_story = serializers.ReadOnlyField()

    class Meta:
        model = UserStory
        fields = [
            'id',
            'title',
            'description',
            'as_a',
            'i_want',
            'so_that',
            'full_story',
            'status',
            'priority',
            'epic',
            'assigned_to',
            'assigned_to_detail',
            'story_points',
            'start_date',
            'due_date',
            'tasks',
            'tasks_count',
            'completion_percentage',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'tasks_count', 'completion_percentage', 'full_story']


class EpicSerializer(serializers.ModelSerializer):
    """Serializer for Epic model"""

    # Nested user stories (read-only)
    user_stories = UserStorySerializer(many=True, read_only=True)

    # Show owner details
    owner_detail = UserSerializer(source='owner', read_only=True)

    # Show computed properties
    user_stories_count = serializers.ReadOnlyField()
    completion_percentage = serializers.ReadOnlyField()

    class Meta:
        model = Epic
        fields = [
            'id',
            'title',
            'description',
            'status',
            'priority',
            'owner',
            'owner_detail',
            'start_date',
            'due_date',
            'user_stories',
            'user_stories_count',
            'completion_percentage',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'user_stories_count', 'completion_percentage']

        # Simplified serializers (without nested data) for list views


class EpicListSerializer(serializers.ModelSerializer):
    """Simplified Epic serializer for list view"""

    owner_detail = UserSerializer(source='owner', read_only=True)
    user_stories_count = serializers.ReadOnlyField()
    completion_percentage = serializers.ReadOnlyField()

    class Meta:
        model = Epic
        fields = [
            'id',
            'title',
            'status',
            'priority',
            'owner',
            'owner_detail',
            'user_stories_count',
            'completion_percentage',
            'due_date',
            'created_at',
        ]


class UserStoryListSerializer(serializers.ModelSerializer):
    """Simplified UserStory serializer for list view"""

    assigned_to_detail = UserSerializer(source='assigned_to', read_only=True)
    tasks_count = serializers.ReadOnlyField()
    completion_percentage = serializers.ReadOnlyField()

    class Meta:
        model = UserStory
        fields = [
            'id',
            'title',
            'status',
            'priority',
            'epic',
            'assigned_to',
            'assigned_to_detail',
            'story_points',
            'tasks_count',
            'completion_percentage',
            'due_date',
            'created_at',
        ]
