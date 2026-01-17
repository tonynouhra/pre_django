from django.contrib import admin
from .models import Epic, UserStory, Task


@admin.register(Epic)
class EpicAdmin(admin.ModelAdmin):
    """Admin configuration for Epic model"""

    list_display = [
        'title',
        'status',
        'priority',
        'owner',
        'user_stories_count',
        'completion_percentage',
        'due_date',
        'created_at'
    ]

    list_filter = ['status', 'priority', 'created_at', 'owner']
    search_fields = ['title', 'description']

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'owner')
        }),
        ('Status & Priority', {
            'fields': ('status', 'priority')
        }),
        ('Dates', {
            'fields': ('start_date', 'due_date')
        }),
    )

    readonly_fields = ['created_at', 'updated_at']

    def user_stories_count(self, obj):
        return obj.user_stories_count

    user_stories_count.short_description = 'User Stories'

    def completion_percentage(self, obj):
        return f"{obj.completion_percentage}%"

    completion_percentage.short_description = 'Completion'


@admin.register(UserStory)
class UserStoryAdmin(admin.ModelAdmin):
    """Admin configuration for UserStory model"""

    list_display = [
        'title',
        'epic',
        'status',
        'priority',
        'assigned_to',
        'story_points',
        'tasks_count',
        'completion_percentage',
        'due_date'
    ]

    list_filter = ['status', 'priority', 'epic', 'assigned_to', 'created_at']
    search_fields = ['title', 'description', 'as_a', 'i_want', 'so_that']

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'epic')
        }),
        ('User Story Format (Optional)', {
            'fields': ('as_a', 'i_want', 'so_that'),
            'description': 'Agile format: As a [user], I want [goal], so that [benefit]'
        }),
        ('Status & Assignment', {
            'fields': ('status', 'priority', 'assigned_to', 'story_points')
        }),
        ('Dates', {
            'fields': ('start_date', 'due_date')
        }),
    )

    readonly_fields = ['created_at', 'updated_at']

    def tasks_count(self, obj):
        return obj.tasks_count

    tasks_count.short_description = 'Tasks'

    def completion_percentage(self, obj):
        return f"{obj.completion_percentage}%"

    completion_percentage.short_description = 'Completion'


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Admin configuration for Task model"""

    list_display = [
        'title',
        'user_story',
        'status',
        'priority',
        'assigned_to',
        'estimated_hours',
        'actual_hours',
        'is_overdue',
        'due_date',
        'created_at'
    ]

    list_filter = ['status', 'priority', 'user_story__epic', 'assigned_to', 'created_at']
    search_fields = ['title', 'description', 'user_story__title']

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'user_story')
        }),
        ('Status & Assignment', {
            'fields': ('status', 'priority', 'assigned_to')
        }),
        ('Time Tracking', {
            'fields': ('estimated_hours', 'actual_hours')
        }),
        ('Dates', {
            'fields': ('due_date', 'completed_at')
        }),
    )

    readonly_fields = ['created_at', 'updated_at']

    def is_overdue(self, obj):
        return '🔴 Yes' if obj.is_overdue else '✅ No'

    is_overdue.short_description = 'Overdue'