# Django Task Manager API - Setup Guide

## Project Overview
Building a Task Manager REST API using Django REST Framework for job assessment.
**Background**: Experience with Flask/FastAPI, learning Django patterns.

---

## Part 1: Environment Setup

### Step 1: Create Virtual Environment
```bash
python3 -m venv venv
```

### Step 2: Activate Virtual Environment
```bash
# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### Step 3: Install Core Packages
```bash
pip install django djangorestframework djangorestframework-simplejwt django-cors-headers python-decouple psycopg2-binary
```

### Step 4: Create requirements.txt
```bash
pip freeze > requirements.txt
```

---

## Part 2: Django Project Setup

### Step 1: Create Django Project
```bash
django-admin startproject taskmanager .
```
The `.` creates the project in the current directory.

**Project Structure:**
```
taskmanager/
├── taskmanager/
│   ├── __init__.py
│   ├── settings.py     # Configuration
│   ├── urls.py         # URL routing
│   ├── asgi.py
│   └── wsgi.py
├── manage.py           # Django CLI tool
└── venv/
```

### Step 2: Create .gitignore
Create `.gitignore` in project root:

```gitignore
# Environment variables
.env

# Virtual environment
venv/
env/

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python

# Django
*.log
db.sqlite3
db.sqlite3-journal
media/

# IDE
.vscode/
.idea/
*.swp
*.swo
```

---

## Part 3: PostgreSQL Database Configuration

### Step 1: Create PostgreSQL Database

**Option A - Using psql (Command Line):**
```bash
# Access PostgreSQL
psql postgres

# Inside psql, run:
CREATE DATABASE taskmanager_db;
CREATE USER taskmanager_user WITH PASSWORD 'your_secure_password';
ALTER ROLE taskmanager_user SET client_encoding TO 'utf8';
ALTER ROLE taskmanager_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE taskmanager_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE taskmanager_db TO taskmanager_user;

# Exit psql
\q
```

**Option B - Using pgAdmin GUI:**
- Create database: `taskmanager_db`
- Create user: `taskmanager_user` with a password

### Step 2: Create .env File
Create `.env` file in project root:

```env
SECRET_KEY=your-django-secret-key-here
DEBUG=True

# PostgreSQL Database
DB_NAME=taskmanager_db
DB_USER=taskmanager_user
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432
```

### Step 3: Update settings.py
Open `taskmanager/settings.py`:

**Add at the top (after imports):**
```python
from decouple import config
import os
```

**Update SECRET_KEY and DEBUG:**
```python
SECRET_KEY = config('SECRET_KEY', default='django-insecure-fallback-key')
DEBUG = config('DEBUG', default=False, cast=bool)
```

**Replace DATABASES section (around line 75-85):**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}
```

---

## Part 4: Custom User Model Setup

⚠️ **IMPORTANT: Do this BEFORE running first migration!**

### Step 1: Create Accounts App
```bash
python manage.py startapp accounts
```

**Creates structure:**
```
accounts/
├── __init__.py
├── admin.py
├── apps.py
├── models.py
├── tests.py
└── views.py
```

### Step 2: Register App in settings.py
Open `taskmanager/settings.py`, find `INSTALLED_APPS` and add:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Your apps
    'accounts',  # Add this line
]
```

### Step 3: Create Custom User Model
Open `accounts/models.py` and replace with:

```python
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """
    Custom User Model extending Django's AbstractUser
    Adds additional fields: age, phone_number, bio
    """

    # Custom fields
    age = models.IntegerField(null=True, blank=True, help_text="User's age")
    phone_number = models.CharField(max_length=15, blank=True, help_text="Contact number")
    bio = models.TextField(blank=True, help_text="User biography")

    # Make email required and unique
    email = models.EmailField(unique=True, help_text="Email address")

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
```

### Step 4: Configure Custom User Model
Open `taskmanager/settings.py` and add at the bottom:

```python
# Custom User Model
AUTH_USER_MODEL = 'accounts.CustomUser'
```

### Step 5: Register in Admin Panel
Open `accounts/admin.py` and replace with:

```python
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    """Custom User Admin panel configuration"""

    model = CustomUser

    # Fields to display in user list
    list_display = ['username', 'email', 'first_name', 'last_name', 'age', 'is_staff']

    # Add custom fields to the admin form
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('age', 'phone_number', 'bio')}),
    )

    # Fields when creating new user
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('age', 'phone_number', 'bio', 'email')}),
    )


admin.site.register(CustomUser, CustomUserAdmin)
```

---

## Part 5: Database Migrations & Testing

### Step 1: Delete Old Database (if exists)
⚠️ **Only if you already ran migrations before setting up CustomUser!**

```bash
# For SQLite
rm db.sqlite3

# For PostgreSQL (in psql)
DROP DATABASE taskmanager_db;
CREATE DATABASE taskmanager_db;
GRANT ALL PRIVILEGES ON DATABASE taskmanager_db TO taskmanager_user;
\q
```

### Step 2: Create Migrations
```bash
python manage.py makemigrations
```

**Expected output:**
```
Migrations for 'accounts':
  accounts/migrations/0001_initial.py
    - Create model CustomUser
```

### Step 3: Apply Migrations
```bash
python manage.py migrate
```

This creates all tables in PostgreSQL including CustomUser.

### Step 4: Create Superuser
```bash
python manage.py createsuperuser
```

**You'll be prompted for:**
- Username
- Email (required!)
- Password
- Age, phone_number, bio (optional)

### Step 5: Start Development Server
```bash
python manage.py runserver
```

### Step 6: Access Django Admin
Open browser: `http://127.0.0.1:8000/admin`

**You should see:**
- Accounts section
- Users with custom fields (age, phone_number, bio)

### Step 7: Verify PostgreSQL Connection
```bash
python manage.py dbshell
```

This connects to PostgreSQL. Type `\q` to exit.

---

## Quick Reference Commands

### Virtual Environment
```bash
source venv/bin/activate              # Activate (macOS/Linux)
deactivate                            # Deactivate
pip freeze > requirements.txt         # Save packages
pip install -r requirements.txt       # Install packages
```

### Django Management
```bash
python manage.py runserver            # Start dev server
python manage.py makemigrations       # Create migrations
python manage.py migrate              # Apply migrations
python manage.py createsuperuser      # Create admin user
python manage.py startapp <name>      # Create new app
python manage.py dbshell              # Access database shell
python manage.py shell                # Python shell with Django
```

### Git
```bash
git init                              # Initialize repo
git add .                             # Stage all changes
git commit -m "message"               # Commit changes
git status                            # Check status
```

---

## Key Concepts: Django vs Flask/FastAPI

### Project Structure
- **Django Project**: Container for entire app (settings, URLs, WSGI)
- **Django Apps**: Modular components (like Flask blueprints)
- More opinionated structure than Flask/FastAPI

### Models & ORM
- Django ORM is built-in (vs SQLAlchemy in Flask)
- Migrations are integrated (vs Alembic)
- Models define database schema

### Django REST Framework
- **Serializers**: Validate & transform data (like Pydantic in FastAPI)
- **ViewSets**: Handle CRUD operations (like Flask views or FastAPI routes)
- **Routers**: Auto-generate URL patterns

### Authentication
- Built-in user authentication
- Using JWT with `djangorestframework-simplejwt`
- Similar to Flask-JWT or FastAPI OAuth2

### Admin Panel
- Auto-generated admin interface
- Register models to manage them visually
- No equivalent in Flask/FastAPI (must build manually)

---

## What We've Accomplished ✅

1. ✅ Created virtual environment
2. ✅ Installed Django, DRF, and dependencies
3. ✅ Created Django project structure
4. ✅ Configured PostgreSQL database
5. ✅ Created Custom User Model with age, phone_number, bio
6. ✅ Registered CustomUser in admin panel
7. ✅ Applied migrations to PostgreSQL
8. ✅ Created superuser
9. ✅ Tested admin panel with custom fields

---

## Next Steps 🚀

1. Create Task app (`python manage.py startapp tasks`)
2. Create Task model (title, description, status, priority, due_date)
3. Create serializers for Task and User
4. Create ViewSets for CRUD operations
5. Configure URL routing
6. Add JWT authentication
7. Write API tests
8. Add permissions (users can only see their own tasks)
9. Document API with drf-spectacular

---

## Important Notes 💡

- **CustomUser** must be created BEFORE first migration
- User and Task are separate models (connected via ForeignKey)
- Always activate virtual environment before working
- Use `.env` file for sensitive data (never commit to Git)
- Run migrations after every model change
- Admin panel is at `/admin` endpoint
- API endpoints will be at `/api/` (we'll configure this)

---

## Common Issues & Solutions

### Issue: psycopg2 installation fails
**Solution:** Install PostgreSQL development headers:
```bash
# macOS
brew install postgresql

# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib libpq-dev
```

### Issue: Migration conflicts
**Solution:** Delete migrations and database, recreate:
```bash
rm -rf accounts/migrations/
python manage.py makemigrations accounts
python manage.py migrate
```

### Issue: Can't login to admin
**Solution:** Create new superuser:
```bash
python manage.py createsuperuser
```

---

## Project Structure (Current)

```
taskmanager/
├── accounts/                  # User management app
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py              # CustomUser admin config
│   ├── apps.py
│   ├── models.py             # CustomUser model
│   ├── tests.py
│   └── views.py
├── taskmanager/              # Project settings
│   ├── __init__.py
│   ├── settings.py           # Configuration
│   ├── urls.py               # URL routing
│   ├── asgi.py
│   └── wsgi.py
├── venv/                     # Virtual environment
├── .env                      # Environment variables (secret!)
├── .gitignore               # Git ignore rules
├── manage.py                # Django CLI
└── requirements.txt         # Python packages
```

---

## Part 6: Creating Task Management Models (Epic → UserStory → Task)

### Understanding the Hierarchy

**Agile Project Structure:**
```
Epic (Highest level - big feature)
  └── User Story (Mid-level - user requirement)
      └── Task (Lowest level - actionable work item)
```

**Example:**
```
Epic: "User Authentication System"
  └── User Story: "As a user, I want to login with email/password"
      └── Task: "Create login form component"
      └── Task: "Implement JWT authentication"
      └── Task: "Write authentication tests"
```

---

### Step 1: Create Tasks App

```bash
python manage.py startapp tasks
```

**Creates structure:**
```
tasks/
├── __init__.py
├── admin.py
├── apps.py
├── models.py
├── tests.py
└── views.py
```

---

### Step 2: Register App in settings.py

Open `taskmanager/settings.py`, find `INSTALLED_APPS` and add:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third party
    'rest_framework',
    'corsheaders',
    'django_filters',

    # Your apps
    'accounts',
    'tasks',  # Add this line
]
```

---

### Step 3: Create Models

Open `tasks/models.py` - Create three models:

**Epic Model:**
```python
from django.db import models
from django.conf import settings

class Epic(models.Model):
    """Highest level container for related user stories"""

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

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='TODO')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='MEDIUM')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='epics')

    start_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def user_stories_count(self):
        return self.user_stories.count()

    @property
    def completion_percentage(self):
        total = self.user_stories.count()
        if total == 0:
            return 0
        done = self.user_stories.filter(status='DONE').count()
        return round((done / total) * 100, 2)

    def __str__(self):
        return f"{self.title} ({self.status})"
```

**UserStory Model:**
```python
class UserStory(models.Model):
    """Mid-level work item - user requirement"""

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

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Agile format
    as_a = models.CharField(max_length=100, blank=True)
    i_want = models.CharField(max_length=200, blank=True)
    so_that = models.CharField(max_length=200, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='TODO')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='MEDIUM')

    epic = models.ForeignKey(Epic, on_delete=models.CASCADE, related_name='user_stories')
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_stories')

    story_points = models.IntegerField(null=True, blank=True)

    start_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def tasks_count(self):
        return self.tasks.count()

    @property
    def completion_percentage(self):
        total = self.tasks.count()
        if total == 0:
            return 0
        done = self.tasks.filter(status='DONE').count()
        return round((done / total) * 100, 2)

    def __str__(self):
        return f"{self.title} - {self.epic.title}"
```

**Task Model:**
```python
class Task(models.Model):
    """Lowest level work item - actionable task"""

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

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='TODO')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='MEDIUM')

    user_story = models.ForeignKey(UserStory, on_delete=models.CASCADE, related_name='tasks')
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')

    estimated_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    actual_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    due_date = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_overdue(self):
        from django.utils import timezone
        if self.due_date and self.status != 'DONE':
            return timezone.now() > self.due_date
        return False

    def __str__(self):
        return f"{self.title} - {self.user_story.title}"
```

---

### Step 4: Register in Admin Panel

Open `tasks/admin.py`:

```python
from django.contrib import admin
from .models import Epic, UserStory, Task

@admin.register(Epic)
class EpicAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'priority', 'owner', 'user_stories_count', 'completion_percentage', 'created_at']
    list_filter = ['status', 'priority', 'owner']
    search_fields = ['title', 'description']

@admin.register(UserStory)
class UserStoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'epic', 'status', 'priority', 'assigned_to', 'tasks_count', 'completion_percentage']
    list_filter = ['status', 'priority', 'epic']
    search_fields = ['title', 'description']

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'user_story', 'status', 'priority', 'assigned_to', 'is_overdue', 'created_at']
    list_filter = ['status', 'priority', 'assigned_to']
    search_fields = ['title', 'description']
```

---

### Step 5: Create and Apply Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## Part 7: Creating REST API

### Understanding Django App Files

| File | Purpose | Similar To |
|------|---------|------------|
| **models.py** | Database schema | SQLAlchemy / Pydantic models |
| **serializers.py** | Data validation & JSON conversion | Pydantic schemas |
| **views.py** | Request handlers (API endpoints) | Flask routes / FastAPI endpoints |
| **urls.py** | URL routing | Flask blueprints / FastAPI router |
| **admin.py** | Admin panel config | Flask-Admin |
| **tests.py** | Unit tests | pytest / unittest |
| **apps.py** | App configuration | Flask app factory |

---

### Step 1: Configure Django REST Framework

Open `taskmanager/settings.py` and add to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ... existing apps

    # Third party
    'rest_framework',
    'corsheaders',
    'django_filters',  # For filtering API

    # Your apps
    'accounts',
    'tasks',
]
```

**Add REST Framework settings at bottom of settings.py:**

```python
# Django REST Framework Settings
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',  # Open to all for now
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}
```

**Install django-filter:**
```bash
pip install django-filter
pip freeze > requirements.txt
```

---

### Step 2: Create Serializers

Create new file: `tasks/serializers.py`

```python
from rest_framework import serializers
from .models import Epic, UserStory, Task
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User (simplified)"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class TaskSerializer(serializers.ModelSerializer):
    """Task serializer with nested user details"""
    assigned_to_detail = UserSerializer(source='assigned_to', read_only=True)
    is_overdue = serializers.ReadOnlyField()

    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserStorySerializer(serializers.ModelSerializer):
    """UserStory serializer with nested tasks"""
    tasks = TaskSerializer(many=True, read_only=True)
    assigned_to_detail = UserSerializer(source='assigned_to', read_only=True)
    tasks_count = serializers.ReadOnlyField()
    completion_percentage = serializers.ReadOnlyField()

    class Meta:
        model = UserStory
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class EpicSerializer(serializers.ModelSerializer):
    """Epic serializer with nested user stories"""
    user_stories = UserStorySerializer(many=True, read_only=True)
    owner_detail = UserSerializer(source='owner', read_only=True)
    user_stories_count = serializers.ReadOnlyField()
    completion_percentage = serializers.ReadOnlyField()

    class Meta:
        model = Epic
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
```

---

### Step 3: Create ViewSets

Open `tasks/views.py`:

```python
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Epic, UserStory, Task
from .serializers import EpicSerializer, UserStorySerializer, TaskSerializer


class EpicViewSet(viewsets.ModelViewSet):
    """
    API endpoints for Epic model
    Provides: list, create, retrieve, update, destroy
    """
    queryset = Epic.objects.all()
    serializer_class = EpicSerializer

    # Enable filtering, searching, ordering
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'owner']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'due_date', 'priority']
    ordering = ['-created_at']

    @action(detail=True, methods=['get'])
    def user_stories(self, request, pk=None):
        """Get all user stories for this epic"""
        epic = self.get_object()
        user_stories = epic.user_stories.all()
        serializer = UserStorySerializer(user_stories, many=True)
        return Response(serializer.data)


class UserStoryViewSet(viewsets.ModelViewSet):
    """API endpoints for UserStory model"""
    queryset = UserStory.objects.all()
    serializer_class = UserStorySerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'epic', 'assigned_to']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'due_date', 'priority']
    ordering = ['-created_at']

    @action(detail=True, methods=['get'])
    def tasks(self, request, pk=None):
        """Get all tasks for this user story"""
        user_story = self.get_object()
        tasks = user_story.tasks.all()
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)


class TaskViewSet(viewsets.ModelViewSet):
    """API endpoints for Task model"""
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'user_story', 'assigned_to']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'due_date', 'priority']
    ordering = ['-created_at']

    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get all overdue tasks"""
        from django.utils import timezone
        overdue_tasks = Task.objects.filter(
            due_date__lt=timezone.now(),
            status__in=['TODO', 'IN_PROGRESS']
        )
        serializer = self.get_serializer(overdue_tasks, many=True)
        return Response(serializer.data)
```

---

### Step 4: Create URL Routing

Create new file: `tasks/urls.py`

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EpicViewSet, UserStoryViewSet, TaskViewSet

router = DefaultRouter()
router.register(r'epics', EpicViewSet, basename='epic')
router.register(r'user-stories', UserStoryViewSet, basename='userstory')
router.register(r'tasks', TaskViewSet, basename='task')

urlpatterns = [
    path('', include(router.urls)),
]
```

---

### Step 5: Include API URLs in Main Project

Open `taskmanager/urls.py`:

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('tasks.urls')),  # Add this
]
```

---

### Step 6: Test Your API

**Start server:**
```bash
python manage.py runserver
```

**Access API endpoints:**
- `http://127.0.0.1:8000/api/` - API root
- `http://127.0.0.1:8000/api/epics/` - List epics
- `http://127.0.0.1:8000/api/user-stories/` - List user stories
- `http://127.0.0.1:8000/api/tasks/` - List tasks

**DRF provides a browsable API interface - you can test directly in the browser!**

---

## API Endpoints Reference

### Epic Endpoints
```
GET    /api/epics/                     List all epics
POST   /api/epics/                     Create new epic
GET    /api/epics/{id}/                Get epic detail
PUT    /api/epics/{id}/                Update epic (full)
PATCH  /api/epics/{id}/                Update epic (partial)
DELETE /api/epics/{id}/                Delete epic
GET    /api/epics/{id}/user_stories/   Get user stories in epic
```

### UserStory Endpoints
```
GET    /api/user-stories/              List all user stories
POST   /api/user-stories/              Create new user story
GET    /api/user-stories/{id}/         Get user story detail
PUT    /api/user-stories/{id}/         Update user story
PATCH  /api/user-stories/{id}/         Partial update
DELETE /api/user-stories/{id}/         Delete user story
GET    /api/user-stories/{id}/tasks/   Get tasks in user story
```

### Task Endpoints
```
GET    /api/tasks/                     List all tasks
POST   /api/tasks/                     Create new task
GET    /api/tasks/{id}/                Get task detail
PUT    /api/tasks/{id}/                Update task
PATCH  /api/tasks/{id}/                Partial update
DELETE /api/tasks/{id}/                Delete task
GET    /api/tasks/overdue/             Get overdue tasks
```

---

## Filtering & Search Examples

```bash
# Filter by status
GET /api/epics/?status=TODO

# Filter by priority
GET /api/tasks/?priority=HIGH

# Search
GET /api/epics/?search=authentication

# Filter by relationship
GET /api/user-stories/?epic=1
GET /api/tasks/?user_story=2

# Multiple filters
GET /api/tasks/?status=TODO&priority=HIGH

# Ordering
GET /api/tasks/?ordering=-created_at
GET /api/epics/?ordering=due_date
```

---

## Updated Project Structure

```
taskmanager/
├── accounts/                  # User management
│   ├── migrations/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py             # CustomUser
│   ├── tests.py
│   └── views.py
├── tasks/                     # Task management
│   ├── migrations/
│   ├── admin.py              # Epic, UserStory, Task admin
│   ├── apps.py
│   ├── models.py             # Epic, UserStory, Task models
│   ├── serializers.py        # DRF serializers (NEW)
│   ├── urls.py               # API routing (NEW)
│   ├── views.py              # API ViewSets
│   └── tests.py
├── taskmanager/              # Project settings
│   ├── settings.py           # Configuration
│   ├── urls.py               # Main URL routing
│   └── wsgi.py
├── .env                      # Environment variables
├── .gitignore
├── manage.py
└── requirements.txt
```

---

## What We've Accomplished ✅

### Part 6: Task Models
1. ✅ Created `tasks` app
2. ✅ Built Epic → UserStory → Task hierarchy
3. ✅ Added status, priority, assignment features
4. ✅ Implemented completion tracking
5. ✅ Registered models in admin panel

### Part 7: REST API
1. ✅ Configured Django REST Framework
2. ✅ Created serializers for data validation
3. ✅ Built ViewSets for CRUD operations
4. ✅ Set up URL routing
5. ✅ Added filtering, searching, ordering
6. ✅ Created custom actions (user_stories, tasks, overdue)
7. ✅ Enabled browsable API interface

---

## Next Steps 🚀

1. Add JWT authentication
2. Add permissions (users can only see their own data)
3. Create user registration/login endpoints
4. Write comprehensive tests
5. Add API documentation with drf-spectacular
6. Implement pagination properly
7. Add validation rules
8. Create Docker setup