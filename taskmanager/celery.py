import os
from celery import Celery
from celery.schedules import crontab

# Set default Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taskmanager.settings')

app = Celery('taskmanager')

# Load config from Django settings with CELERY prefix
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all installed apps
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'send-overdue-reminders-daily': {
        'task': 'tasks.tasks.send_overdue_task_reminders',
        'schedule': crontab(hour=9, minute=0),# Send daily overdue task reminders at 9 AM
    }

}


@app.task(bind=True)


def debug_task(self):
    print(f'Request: {self.request!r}')
