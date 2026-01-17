# Redis, Celery & Email Notifications Setup

## Overview
Implemented asynchronous email notifications using Redis and Celery. When the status of an Epic, UserStory, or Task changes, an email is automatically sent to the owner/assigned user and the reporter.

---

## 1. Packages Installed

```bash
pip install redis celery django-celery-beat django-celery-results
```

---

## 2. Celery Configuration

### File: `taskmanager/celery.py`
Created Celery application configuration:

```python
import os
from celery import Celery

# Set default Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taskmanager.settings')

app = Celery('taskmanager')

# Load config from Django settings with CELERY prefix
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all installed apps
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
```

### File: `taskmanager/__init__.py`
Import Celery app when Django starts:

```python
# This will make sure the app is always imported when Django starts
from .celery import app as celery_app

__all__ = ('celery_app',)
```

---

## 3. Django Settings Configuration

### File: `taskmanager/settings.py`

#### Celery Settings:
```python
# Celery Configuration
CELERY_BROKER_URL = 'redis://localhost:6379/0'  # Redis as message broker
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'  # Store task results in Redis
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
```

#### Email Settings (Mailtrap):
```python
# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'sandbox.smtp.mailtrap.io'
EMAIL_PORT = 587  # IMPORTANT: Use 587 for TLS
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = 'noreply@taskmanager.com'
```

#### Alternative - Console Backend (Development):
```python
# For development testing (prints email to console)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

---

## 4. Environment Variables

### File: `.env`
Add Mailtrap credentials:

```bash
EMAIL_HOST_USER=your_mailtrap_username
EMAIL_HOST_PASSWORD=your_mailtrap_password
```

Example:
```bash
EMAIL_HOST_USER=0f10f597e9432a
EMAIL_HOST_PASSWORD=b5506b82e17fc8
```

---

## 5. Celery Tasks

### File: `tasks/tasks.py`
Created async task to send status change emails:

```python
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Epic, UserStory, Task


@shared_task
def send_status_change_email(model_name, instance_id, old_status, new_status):
    """
    Send email notification when Epic/UserStory/Task status changes

    Args:
        model_name: 'Epic', 'UserStory', or 'Task'
        instance_id: ID of the changed instance
        old_status: Previous status
        new_status: New status
    """
    # Get the model class
    model_map = {
        'Epic': Epic,
        'UserStory': UserStory,
        'Task': Task,
    }

    model_class = model_map.get(model_name)
    if not model_class:
        return f"Invalid model name: {model_name}"

    try:
        instance = model_class.objects.get(id=instance_id)
    except model_class.DoesNotExist:
        return f"{model_name} with id {instance_id} not found"

    # Collect recipients
    recipients = []

    # Add owner/assigned_to email
    if hasattr(instance, 'owner') and instance.owner and instance.owner.email:
        recipients.append(instance.owner.email)
    elif hasattr(instance, 'assigned_to') and instance.assigned_to and instance.assigned_to.email:
        recipients.append(instance.assigned_to.email)

    # Add reporter email
    if instance.reporter and instance.reporter.email:
        recipients.append(instance.reporter.email)

    # Remove duplicates
    recipients = list(set(recipients))

    if not recipients:
        return "No recipients with valid email addresses"

    # Prepare email
    subject = f"{model_name} Status Changed: {instance.title}"
    message = f"""
    Hello,

    The status of {model_name} "{instance.title}" has been changed:

    Previous Status: {old_status}
    New Status: {new_status}

    {model_name} Details:
    - Title: {instance.title}
    - Priority: {instance.priority}
    - Status: {new_status}

    Best regards,
    Task Manager System
    """

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipients,
            fail_silently=False,
        )
        return f"Email sent successfully to {', '.join(recipients)}"
    except Exception as e:
        return f"Failed to send email: {str(e)}"
```

---

## 6. Django Signals

### File: `tasks/signals.py`
Signals to detect status changes and trigger email tasks:

```python
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import Epic, UserStory, Task
from .tasks import send_status_change_email


def get_old_instance(model_class, instance):
    """Get the old instance from database before save"""
    try:
        return model_class.objects.get(pk=instance.pk)
    except model_class.DoesNotExist:
        return None


# Epic Signals
@receiver(pre_save, sender=Epic)
def epic_pre_save(sender, instance, **kwargs):
    """Store old status before Epic is saved"""
    if instance.pk:
        old_instance = get_old_instance(Epic, instance)
        if old_instance:
            instance._old_status = old_instance.status
        else:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=Epic)
def epic_post_save(sender, instance, created, **kwargs):
    """Send email if Epic status changed"""
    if not created and hasattr(instance, '_old_status'):
        old_status = instance._old_status
        new_status = instance.status

        if old_status and old_status != new_status:
            # Trigger async task
            send_status_change_email.delay(
                model_name='Epic',
                instance_id=instance.id,
                old_status=old_status,
                new_status=new_status
            )


# UserStory Signals
@receiver(pre_save, sender=UserStory)
def userstory_pre_save(sender, instance, **kwargs):
    """Store old status before UserStory is saved"""
    if instance.pk:
        old_instance = get_old_instance(UserStory, instance)
        if old_instance:
            instance._old_status = old_instance.status
        else:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=UserStory)
def userstory_post_save(sender, instance, created, **kwargs):
    """Send email if UserStory status changed"""
    if not created and hasattr(instance, '_old_status'):
        old_status = instance._old_status
        new_status = instance.status

        if old_status and old_status != new_status:
            send_status_change_email.delay(
                model_name='UserStory',
                instance_id=instance.id,
                old_status=old_status,
                new_status=new_status
            )


# Task Signals
@receiver(pre_save, sender=Task)
def task_pre_save(sender, instance, **kwargs):
    """Store old status before Task is saved"""
    if instance.pk:
        old_instance = get_old_instance(Task, instance)
        if old_instance:
            instance._old_status = old_instance.status
        else:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=Task)
def task_post_save(sender, instance, created, **kwargs):
    """Send email if Task status changed"""
    if not created and hasattr(instance, '_old_status'):
        old_status = instance._old_status
        new_status = instance.status

        if old_status and old_status != new_status:
            send_status_change_email.delay(
                model_name='Task',
                instance_id=instance.id,
                old_status=old_status,
                new_status=new_status
            )
```

### File: `tasks/apps.py`
Register signals when app is ready:

```python
from django.apps import AppConfig


class TasksConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "tasks"

    def ready(self):
        import tasks.signals  # Register signals
```

---

## 7. How It Works

### Flow:
1. **User changes status** (via Django Admin or REST API)
2. **pre_save signal fires** → Captures old status from database
3. **Django saves the model** → Status updated in database
4. **post_save signal fires** → Compares old vs new status
5. **If status changed** → Triggers Celery task asynchronously
6. **Celery task executes** → Sends email to owner/assigned user and reporter
7. **Email delivered** → Via Mailtrap SMTP or console backend

### Key Points:
- **Asynchronous**: Email sending doesn't block the request
- **Automatic**: Works in Admin, API, Django shell - anywhere `.save()` is called
- **Flexible**: Easily extendable to other models or notification types

---

## 8. Running the System

### Terminal 1 - Redis Server:
```bash
redis-server
```

### Terminal 2 - Celery Worker:
```bash
cd /Users/tonynouhra/Documents/MyProjects/pre_django
source venv/bin/activate
celery -A taskmanager worker --loglevel=info
```

### Terminal 3 - Django Server:
```bash
cd /Users/tonynouhra/Documents/MyProjects/pre_django
source venv/bin/activate
python manage.py runserver
```

---

## 9. Testing

### Test via Django Admin:
1. Go to `http://localhost:8000/admin/`
2. Edit any Epic/UserStory/Task
3. Change the status field
4. Click Save
5. Check Celery worker logs for task execution
6. Check Mailtrap inbox for email

### Test via REST API:
```bash
# Change Epic status
curl -X PATCH http://localhost:8000/api/epics/1/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{"status": "IN_PROGRESS"}'
```

### Expected Celery Output:
```
[2026-01-17 22:15:00,000: INFO/MainProcess] Task tasks.tasks.send_status_change_email received
[2026-01-17 22:15:00,123: INFO/ForkPoolWorker-8] Task succeeded: 'Email sent successfully to user@example.com'
```

---

## 10. Troubleshooting

### Celery Worker Not Running:
- Make sure virtual environment is activated
- Check Redis is running: `redis-cli ping` (should return PONG)
- Verify Celery sees your tasks: `celery -A taskmanager inspect registered`

### Emails Not Sending:
- Check EMAIL_BACKEND in settings.py
- Verify Mailtrap credentials in .env file
- Check EMAIL_PORT is 587 (not 25)
- Restart Celery worker after changing settings
- Check Celery logs for error messages

### Signals Not Firing:
- Verify `tasks.signals` is imported in `tasks/apps.py`
- Check that `tasks` app is in INSTALLED_APPS
- Make sure you're updating existing records (not creating new ones)
- Use Django shell to test: Change status and call `.save()`

---

## 11. Email Recipients Logic

### Epic:
- **Owner** (Epic.owner) - receives email
- **Reporter** (Epic.reporter) - receives email if different from owner

### UserStory:
- **Assigned User** (UserStory.assigned_to) - receives email
- **Reporter** (UserStory.reporter) - receives email if different from assigned user

### Task:
- **Assigned User** (Task.assigned_to) - receives email
- **Reporter** (Task.reporter) - receives email if different from assigned user

### Important:
- Duplicates are automatically removed
- Only users with valid email addresses receive notifications
- If owner/assigned user == reporter, only one email is sent

---

## 12. Production Considerations

### Use Real SMTP Server:
Replace Mailtrap with Gmail, SendGrid, AWS SES, etc.

Example for Gmail:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'  # Use App Password, not regular password
DEFAULT_FROM_EMAIL = 'your-email@gmail.com'
```

### Redis in Production:
- Use managed Redis service (AWS ElastiCache, Redis Cloud, etc.)
- Configure password authentication
- Update CELERY_BROKER_URL with credentials

### Celery in Production:
- Use process manager (systemd, supervisor)
- Configure multiple workers for concurrency
- Set up monitoring and error logging
- Use Celery Beat for periodic tasks

---

## Summary

✅ Redis installed and running as message broker
✅ Celery configured for async task processing
✅ Django signals detect status changes automatically
✅ Email notifications sent to owners and reporters
✅ Works in Admin panel, REST API, and Django shell
✅ Mailtrap configured for testing emails

The system now automatically sends email notifications whenever Epic, UserStory, or Task status changes!