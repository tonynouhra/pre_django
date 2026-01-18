# Task Manager - Django REST API

A production-ready Django REST API for managing projects with Epics, User Stories, and Tasks. Built with modern Python practices, comprehensive testing, and Docker containerization.

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.2-green.svg)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.16-red.svg)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-7-red.svg)](https://redis.io/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-blue.svg)](https://github.com/features/actions)
[![Tests](https://img.shields.io/badge/Tests-113%20Passing-brightgreen.svg)]()
[![Coverage](https://img.shields.io/badge/Coverage-90%25-brightgreen.svg)]()

---

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Docker Setup (Recommended)](#docker-setup-recommended)
  - [Local Development](#local-development)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [CI/CD Pipeline](#cicd-pipeline)
- [Asynchronous Tasks](#asynchronous-tasks)
- [Authentication](#authentication)
- [Contributing](#contributing)
- [License](#license)

---

## ✨ Features

### Core Functionality
- **Hierarchical Project Management**: Epic → User Story → Task relationship structure
- **RESTful API**: Full CRUD operations with filtering, searching, and pagination
- **User Authentication**: JWT-based authentication with access and refresh tokens
- **Asynchronous Tasks**: Celery for background email notifications and scheduled tasks
- **Status Workflow**: Predefined status transitions for Tasks, User Stories, and Epics
- **Email Notifications**: Automated emails on status changes
- **Reporter/Assignee System**: Track who created and who is responsible for each task

### Technical Highlights
- **Type Hints**: Full Python type annotations throughout the codebase
- **Comprehensive Testing**: 90% code coverage with 113+ tests using pytest
- **Docker Containerization**: Multi-service setup with docker-compose
- **Database Design**: PostgreSQL with foreign key relationships and constraints
- **Code Quality**: Follows Django best practices and PEP 8 standards
- **API Documentation**: Auto-generated with drf-spectacular (OpenAPI/Swagger)

---

## 🛠 Tech Stack

### Backend
- **Python 3.11** - Modern Python with type hints
- **Django 5.2** - Web framework
- **Django REST Framework 3.16** - API toolkit
- **PostgreSQL 15** - Primary database
- **Redis 7** - Message broker and caching

### Asynchronous Processing
- **Celery 5.3** - Distributed task queue
- **Celery Beat** - Periodic task scheduler
- **Django Celery Beat** - Database-backed schedules

### Testing & Quality
- **pytest 7.4** - Testing framework
- **pytest-django** - Django integration for pytest
- **Factory Boy** - Test data generation
- **pytest-cov** - Code coverage reporting (90% coverage)
- **Faker** - Realistic test data

### Deployment & DevOps
- **Docker & Docker Compose** - Containerization
- **Gunicorn** - Production WSGI server
- **python-decouple** - Environment variable management

### Additional Tools
- **djangorestframework-simplejwt** - JWT authentication
- **django-filter** - Advanced filtering
- **django-cors-headers** - CORS support
- **drf-spectacular** - API documentation

---

## 📁 Project Structure

```
pre_django/
├── taskmanager/              # Django project settings
│   ├── settings.py           # Main settings with environment variables
│   ├── urls.py               # Root URL configuration
│   ├── celery.py            # Celery configuration
│   └── wsgi.py              # WSGI application
│
├── tasks/                    # Tasks app (core functionality)
│   ├── models.py            # Epic, UserStory, Task models
│   ├── views.py             # API ViewSets
│   ├── serializers.py       # DRF serializers
│   ├── urls.py              # API routes
│   ├── tasks.py             # Celery tasks
│   ├── signals.py           # Django signals for notifications
│   └── tests/               # Comprehensive test suite
│       ├── factories.py     # Factory Boy factories
│       ├── test_models.py   # Model tests (48 tests)
│       ├── test_views.py    # API endpoint tests (40 tests)
│       └── test_serializers.py  # Serializer tests (13 tests)
│
├── authentication/           # JWT authentication app
│   ├── views.py             # Login, register, profile endpoints
│   ├── serializers.py       # Auth serializers
│   ├── urls.py              # Auth routes
│   └── tests/               # Authentication tests (18 tests)
│
├── accounts/                 # User accounts app
│   ├── models.py            # Custom User model
│   ├── admin.py             # Django admin configuration
│   └── migrations/          # Database migrations
│
├── docker-compose.yml        # Multi-service Docker setup
├── Dockerfile                # Production-ready image
├── requirements.txt          # Python dependencies
├── pytest.ini               # Pytest configuration
├── conftest.py              # Global test fixtures
├── .env.example             # Environment variables template
│
├── TESTING.md               # Comprehensive testing guide
├── DOCKER.md                # Docker documentation
├── CI_CD.md                 # CI/CD pipeline documentation
└── README.md                # This file
```

---

## 🚀 Getting Started

### Prerequisites

**For Docker Setup (Recommended):**
- Docker Desktop 24.x or higher
- Docker Compose 2.x or higher

**For Local Development:**
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- pip and virtualenv

---

### Installation

#### Option 1: Docker Setup (Recommended)

This is the easiest way to get started. All services (Django, PostgreSQL, Redis, Celery) will be automatically configured.

```bash
# 1. Clone the repository
git clone <repository-url>
cd pre_django

# 2. Copy environment variables
cp .env.example .env

# 3. Build and start all services
docker-compose up --build

# 4. In a new terminal, create a superuser
docker-compose exec web python manage.py createsuperuser

# 5. Access the application
# API: http://localhost:8000/api/
# Admin: http://localhost:8000/admin/
```

**That's it!** All services are now running:
- Django API on port 8000
- PostgreSQL on port 5432
- Redis on port 6379
- Celery Worker (processing tasks)
- Celery Beat (scheduling tasks)

For more Docker commands and troubleshooting, see [DOCKER.md](DOCKER.md).

---

#### Option 2: Local Development

```bash
# 1. Clone the repository
git clone <repository-url>
cd pre_django

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env file with your local configuration

# 5. Start PostgreSQL and Redis
# Make sure PostgreSQL is running on port 5432
# Make sure Redis is running on port 6379

# 6. Run migrations
python manage.py migrate

# 7. Create superuser
python manage.py createsuperuser

# 8. Start Django development server
python manage.py runserver

# 9. In separate terminals, start Celery services
# Terminal 2: Celery Worker
celery -A taskmanager worker --loglevel=info

# Terminal 3: Celery Beat
celery -A taskmanager beat --loglevel=info
```

---

## 📚 API Documentation

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register/` | Register new user |
| POST | `/api/auth/login/` | Login and get JWT tokens |
| POST | `/api/auth/token/refresh/` | Refresh access token |
| GET | `/api/auth/profile/` | Get current user profile |
| PUT/PATCH | `/api/auth/profile/` | Update user profile |

### Task Management Endpoints

#### Epics
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/epics/` | List all epics (supports filtering) |
| POST | `/api/epics/` | Create new epic |
| GET | `/api/epics/{id}/` | Get epic details |
| PUT/PATCH | `/api/epics/{id}/` | Update epic |
| DELETE | `/api/epics/{id}/` | Delete epic |
| GET | `/api/epics/{id}/statistics/` | Get epic statistics |

#### User Stories
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/user-stories/` | List all user stories |
| POST | `/api/user-stories/` | Create new user story |
| GET | `/api/user-stories/{id}/` | Get user story details |
| PUT/PATCH | `/api/user-stories/{id}/` | Update user story |
| DELETE | `/api/user-stories/{id}/` | Delete user story |
| GET | `/api/user-stories/{id}/statistics/` | Get user story statistics |

#### Tasks
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/tasks/` | List all tasks (supports filtering) |
| POST | `/api/tasks/` | Create new task |
| GET | `/api/tasks/{id}/` | Get task details |
| PUT/PATCH | `/api/tasks/{id}/` | Update task |
| DELETE | `/api/tasks/{id}/` | Delete task |
| POST | `/api/tasks/{id}/assign/` | Assign task to user |
| GET | `/api/tasks/overdue/` | Get overdue tasks |

### Filtering and Search

**Filter tasks by status:**
```
GET /api/tasks/?status=IN_PROGRESS
```

**Search tasks by title:**
```
GET /api/tasks/?search=authentication
```

**Filter by assignee:**
```
GET /api/tasks/?assigned_to=1
```

**Combine filters:**
```
GET /api/tasks/?status=TODO&assigned_to=1&search=bug
```

### Authentication

All API endpoints (except registration and login) require JWT authentication:

```bash
# 1. Login to get tokens
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "password"}'

# Response:
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}

# 2. Use access token for authenticated requests
curl -X GET http://localhost:8000/api/tasks/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

### Example API Usage

**Create a new Epic:**
```bash
curl -X POST http://localhost:8000/api/epics/ \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "User Authentication System",
    "description": "Implement complete user authentication",
    "status": "TODO",
    "reporter": 1
  }'
```

**Create a User Story under the Epic:**
```bash
curl -X POST http://localhost:8000/api/user-stories/ \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "User Login",
    "description": "As a user, I want to login",
    "epic": 1,
    "status": "TODO",
    "reporter": 1
  }'
```

**Create a Task under the User Story:**
```bash
curl -X POST http://localhost:8000/api/tasks/ \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Implement JWT authentication",
    "description": "Add JWT token authentication",
    "user_story": 1,
    "assigned_to": 2,
    "reporter": 1,
    "status": "TODO",
    "priority": "HIGH",
    "due_date": "2026-02-01"
  }'
```

---

## 🧪 Testing

This project has comprehensive test coverage (90%) with 113+ tests covering models, views, serializers, and authentication.

### Run All Tests

```bash
# Using Docker
docker-compose exec web pytest

# Local development
pytest
```

### Run Specific Test Files

```bash
# Test models only
pytest tasks/tests/test_models.py

# Test API endpoints only
pytest tasks/tests/test_views.py

# Test authentication
pytest authentication/tests/test_views.py
```

### Run Tests with Coverage

```bash
# Docker
docker-compose exec web pytest --cov=tasks --cov=accounts --cov=authentication --cov-report=html

# Local
pytest --cov=tasks --cov=accounts --cov=authentication --cov-report=html

# Open coverage report
open htmlcov/index.html
```

### Test Statistics

- **Total Tests**: 113+ passing
- **Coverage**: 90%
- **Test Breakdown**:
  - Model tests: 48 tests
  - API endpoint tests: 40 tests
  - Serializer tests: 13 tests
  - Authentication tests: 18 tests

For detailed testing documentation, see [TESTING.md](TESTING.md).

---

## 🔄 CI/CD Pipeline

This project uses **GitHub Actions** for continuous integration and deployment. Every push and pull request triggers automated checks.

### Pipeline Jobs

1. **Code Quality** - Black, isort, flake8 linting
2. **Security Scan** - Vulnerability scanning with Safety
3. **Run Tests** - 113+ tests with 90% coverage (PostgreSQL + Redis services)
4. **Build Docker** - Validate Docker image builds
5. **Deploy** - Placeholder for future deployment automation

### Workflow Triggers

- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

### Running Checks Locally

Before pushing code, run these commands to ensure CI passes:

```bash
# Format code
black .
isort .

# Lint code
flake8 .

# Run tests with coverage
pytest --cov=tasks --cov=accounts --cov=authentication --cov-fail-under=80

# All-in-one check
black . && isort . && flake8 . && pytest --cov-fail-under=80
```

### CI/CD Features

✅ **Automated Testing** - Full test suite on every push
✅ **Code Quality** - Enforce Python best practices
✅ **Security Scanning** - Check for vulnerable dependencies
✅ **Docker Validation** - Ensure images build successfully
✅ **Coverage Reports** - Track code coverage over time

For comprehensive CI/CD documentation, see [CI_CD.md](CI_CD.md).

---

## 🔄 Asynchronous Tasks

This project uses Celery for background task processing and scheduled jobs.

### Email Notifications

Automatic email notifications are sent when:
- Task status changes
- User Story status changes
- Epic status changes
- Task is assigned to a user

Example notification:
```
Subject: Task Status Updated: "Implement JWT authentication"
Body: The task has been updated from TODO to IN_PROGRESS
```

### Celery Tasks

**Send status change notification:**
```python
from tasks.tasks import send_status_change_notification

send_status_change_notification.delay(
    task_id=123,
    old_status='TODO',
    new_status='IN_PROGRESS'
)
```

### Monitor Celery

```bash
# View worker logs (Docker)
docker-compose logs -f celery-worker

# View beat scheduler logs (Docker)
docker-compose logs -f celery-beat

# Check active tasks (Docker)
docker-compose exec celery-worker celery -A taskmanager inspect active

# Purge task queue (Docker)
docker-compose exec celery-worker celery -A taskmanager purge
```

---

## 🔐 Authentication

This project uses JWT (JSON Web Tokens) for authentication.

### Token Lifetimes

- **Access Token**: 60 minutes (configurable in settings)
- **Refresh Token**: 7 days (configurable in settings)

### Authentication Flow

1. **Register** a new user
   ```bash
   POST /api/auth/register/
   {
     "username": "johndoe",
     "email": "john@example.com",
     "password": "securepass123",
     "first_name": "John",
     "last_name": "Doe"
   }
   ```

2. **Login** to get tokens
   ```bash
   POST /api/auth/login/
   {
     "username": "johndoe",
     "password": "securepass123"
   }
   # Returns: { "access": "...", "refresh": "..." }
   ```

3. **Use access token** for API requests
   ```bash
   GET /api/tasks/
   Header: Authorization: Bearer <access-token>
   ```

4. **Refresh access token** when expired
   ```bash
   POST /api/auth/token/refresh/
   {
     "refresh": "<refresh-token>"
   }
   # Returns: { "access": "new-access-token" }
   ```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Code Quality Guidelines

- Follow PEP 8 style guide
- Add type hints to all functions
- Write tests for new features
- Maintain 80%+ code coverage
- Update documentation as needed

---

## 📝 Environment Variables

Key environment variables (see `.env.example` for full list):

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Django debug mode | `True` |
| `SECRET_KEY` | Django secret key | (required) |
| `DB_NAME` | PostgreSQL database name | `taskmanager_db` |
| `DB_USER` | PostgreSQL username | `postgres` |
| `DB_PASSWORD` | PostgreSQL password | `postgres` |
| `DB_HOST` | Database host | `postgres` (Docker) / `localhost` |
| `CELERY_BROKER_URL` | Redis URL for Celery | `redis://redis:6379/0` |
| `EMAIL_HOST_USER` | Email username (Mailtrap) | - |
| `EMAIL_HOST_PASSWORD` | Email password (Mailtrap) | - |

---

## 🐳 Docker Commands Cheat Sheet

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose stop

# Restart specific service
docker-compose restart web

# Run Django commands
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py shell

# Access PostgreSQL
docker-compose exec postgres psql -U postgres -d taskmanager_db

# Access Redis CLI
docker-compose exec redis redis-cli

# Run tests
docker-compose exec web pytest

# Cleanup (removes containers and volumes)
docker-compose down -v
```

For comprehensive Docker documentation, see [DOCKER.md](DOCKER.md).

---

## 📊 Database Schema

```
Epic
├── id (PK)
├── title
├── description
├── status (TODO, IN_PROGRESS, DONE, CANCELLED)
├── reporter (FK → User)
├── created_at
└── updated_at

UserStory
├── id (PK)
├── title
├── description
├── epic (FK → Epic)
├── status (TODO, IN_PROGRESS, DONE, CANCELLED)
├── reporter (FK → User)
├── created_at
└── updated_at

Task
├── id (PK)
├── title
├── description
├── user_story (FK → UserStory)
├── assigned_to (FK → User)
├── reporter (FK → User)
├── status (TODO, IN_PROGRESS, IN_REVIEW, DONE, CANCELLED)
├── priority (LOW, MEDIUM, HIGH, URGENT)
├── due_date
├── created_at
└── updated_at
```

---

## 🎯 Future Enhancements

- [x] CI/CD Pipeline (GitHub Actions) ✅
- [ ] API Rate Limiting
- [ ] Task Comments and Attachments
- [ ] Real-time Notifications (WebSockets)
- [ ] Advanced Reporting Dashboard
- [ ] Task Time Tracking
- [ ] Email Templates with HTML
- [ ] File Upload Support
- [ ] Task Dependencies
- [ ] Sprint Planning Features

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

## 👤 Author

**Your Name**
- GitHub: [@yourusername](https://github.com/yourusername)
- LinkedIn: [Your Name](https://linkedin.com/in/yourname)
- Email: your.email@example.com

---

## 🙏 Acknowledgments

- Django and Django REST Framework communities
- Celery project for async task processing
- Factory Boy for test data generation
- Docker for containerization

---

## 📞 Support

If you have questions or need help:
- Open an issue on GitHub
- Check the [TESTING.md](TESTING.md) for testing documentation
- Check the [DOCKER.md](DOCKER.md) for Docker documentation
- Check the [CI_CD.md](CI_CD.md) for CI/CD pipeline documentation

---

**Built with ❤️ using Django REST Framework**