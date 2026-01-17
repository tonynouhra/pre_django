from django.core.exceptions import ValidationError
from django.db import models

from taskmanager import settings


# Create your models here.
class Epic(models.Model):
    STATUS_CHOICES = [
        ('TODO', 'To Do'),
        ('IN_PROGRESS', 'In Progress'),
        ('DONE', 'Done'),
        ('CANCELLED', 'Cancelled'),
    ]

    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]
    title = models.CharField(max_length=200, help_text="Epic title")
    description = models.TextField(blank=True, help_text="Detailed description")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='TODO')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='MEDIUM')
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='epics',
        help_text="User who created this epic"
    )
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reported_epics',
        help_text="User who reported this epic"
    )
    start_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Epic"
        verbose_name_plural = "Epics"

    def __str__(self):
        return f"{self.title} ({self.status})"

    @property
    def user_stories_count(self):
        """Count of user stories in this epic"""
        return self.user_stories.count()

    @property
    def completion_percentage(self):
        """Calculate completion percentage based on user stories"""
        total = self.user_stories.count()
        if total == 0:
            return 0
        done = self.user_stories.filter(status='DONE').count()
        return round((done / total) * 100, 2)

    # def clean(self):
    #     """Validate that owner and reporter are different"""
    #     if self.owner and self.reporter and self.owner == self.reporter:
    #         raise ValidationError({
    #             'reporter': 'Reporter cannot be the same as the owner.'
    #         })


class UserStory(models.Model):
    """
    User Story: Mid-level work item belonging to an Epic
    Example: "As a user, I want to login with email and password"
    """

    STATUS_CHOICES = [
        ('TODO', 'To Do'),
        ('IN_PROGRESS', 'In Progress'),
        ('DONE', 'Done'),
        ('CANCELLED', 'Cancelled'),
    ]

    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]

    title = models.CharField(max_length=200, help_text="User story title")
    description = models.TextField(blank=True, help_text="User story details")

    # Agile format: "As a [user], I want [goal], so that [benefit]"
    as_a = models.CharField(max_length=100, blank=True, help_text="As a...")
    i_want = models.CharField(max_length=200, blank=True, help_text="I want to...")
    so_that = models.CharField(max_length=200, blank=True, help_text="So that...")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='TODO')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='MEDIUM')

    # Relationships
    epic = models.ForeignKey(
        Epic,
        on_delete=models.CASCADE,
        related_name='user_stories',
        help_text="Epic this user story belongs to"
    )

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_stories',
        help_text="User assigned to this story"
    )
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reported_stories',
        help_text="User who reported this story"
    )

    # Estimation (story points)
    story_points = models.IntegerField(
        null=True,
        blank=True,
        help_text="Effort estimation (Fibonacci: 1, 2, 3, 5, 8, 13)"
    )

    # Dates
    start_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "User Story"
        verbose_name_plural = "User Stories"

    def __str__(self):
        return f"{self.title} - {self.epic.title}"

    @property
    def tasks_count(self):
        """Count of tasks in this user story"""
        return self.tasks.count()

    @property
    def completion_percentage(self):
        """Calculate completion percentage based on tasks"""
        total = self.tasks.count()
        if total == 0:
            return 0
        done = self.tasks.filter(status='DONE').count()
        return round((done / total) * 100, 2)

    @property
    def full_story(self):
        """Returns formatted user story"""
        if self.as_a and self.i_want and self.so_that:
            return f"As a {self.as_a}, I want {self.i_want}, so that {self.so_that}"
        return self.description

    def clean(self):
        """Validate that assigned_to and reporter are different"""
        if self.assigned_to and self.reporter and self.assigned_to == self.reporter:
            raise ValidationError({
                'reporter': 'Reporter cannot be the same as the assigned user.'
            })


class Task(models.Model):
    """
    Task: Lowest level work item belonging to a User Story
    Example: "Create login form component", "Write unit tests for authentication"
    """

    STATUS_CHOICES = [
        ('TODO', 'To Do'),
        ('IN_PROGRESS', 'In Progress'),
        ('DONE', 'Done'),
        ('BLOCKED', 'Blocked'),
        ('CANCELLED', 'Cancelled'),
    ]

    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]

    title = models.CharField(max_length=200, help_text="Task title")
    description = models.TextField(blank=True, help_text="Task details")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='TODO')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='MEDIUM')

    # Relationships
    user_story = models.ForeignKey(
        UserStory,
        on_delete=models.CASCADE,
        related_name='tasks',
        help_text="User story this task belongs to"
    )

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks',
        help_text="User assigned to this task"
    )
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reported_tasks',
        help_text="User who reported this task"
    )

    # Estimation (hours)
    estimated_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Estimated hours to complete"
    )

    actual_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Actual hours spent"
    )

    # Dates
    due_date = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Task"
        verbose_name_plural = "Tasks"

    def __str__(self):
        return f"{self.title} - {self.user_story.title}"

    @property
    def is_overdue(self):
        """Check if task is overdue"""
        from django.utils import timezone
        if self.due_date and self.status != 'DONE':
            return timezone.now() > self.due_date
        return False

    def clean(self):
        """Validate that assigned_to and reporter are different"""
        if self.assigned_to and self.reporter and self.assigned_to == self.reporter:
            raise ValidationError({
                'reporter': 'Reporter cannot be the same as the assigned user.'
            })
