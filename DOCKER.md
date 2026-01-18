# Docker Setup Documentation

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Quick Start](#quick-start)
4. [Services Architecture](#services-architecture)
5. [Environment Variables](#environment-variables)
6. [Common Commands](#common-commands)
7. [Development Workflow](#development-workflow)
8. [Troubleshooting](#troubleshooting)
9. [Production Considerations](#production-considerations)

---

## Overview

This project uses Docker and Docker Compose to containerize the entire application stack, including:

- **Django Web Application** (Python 3.11)
- **PostgreSQL Database** (v15)
- **Redis** (Message broker & cache)
- **Celery Worker** (Async task processing)
- **Celery Beat** (Scheduled tasks)

### Benefits of Using Docker

✅ **Consistency**: Same environment across development, testing, and production
✅ **Isolation**: Each service runs in its own container
✅ **Easy Setup**: One command to start the entire stack
✅ **Portability**: Works on any platform (macOS, Linux, Windows)
✅ **Scalability**: Easy to scale services independently

---

## Prerequisites

### Required Software

1. **Docker Desktop** (includes Docker and Docker Compose)
   - macOS: [Download Docker Desktop for Mac](https://www.docker.com/products/docker-desktop)
   - Windows: [Download Docker Desktop for Windows](https://www.docker.com/products/docker-desktop)
   - Linux: Install Docker Engine and Docker Compose separately

2. **Verify Installation**:
   ```bash
   docker --version
   # Should show: Docker version 24.x.x or higher

   docker-compose --version
   # Should show: Docker Compose version 2.x.x or higher
   ```

---

## Quick Start

### 1. Clone and Setup

```bash
# Navigate to project directory
cd pre_django

# Copy environment variables template
cp .env.example .env

# Edit .env file with your configuration (optional for development)
# Default values work out of the box!
```

### 2. Build and Start Services

```bash
# Build images and start all services
docker-compose up --build

# Or run in detached mode (background)
docker-compose up -d --build
```

### 3. Access the Application

Once all services are running:

- **Django Admin**: http://localhost:8000/admin/
- **API Endpoints**: http://localhost:8000/api/
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

### 4. Create Superuser

```bash
# Create Django superuser
docker-compose exec web python manage.py createsuperuser
```

### 5. Stop Services

```bash
# Stop all services (keeps data)
docker-compose stop

# Stop and remove containers (keeps data in volumes)
docker-compose down

# Stop and remove everything including volumes (DELETES DATA!)
docker-compose down -v
```

---

## Services Architecture

### Service Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Docker Network                          │
│                                                             │
│  ┌─────────┐   ┌──────────┐   ┌──────┐   ┌──────────┐   │
│  │  Django │   │PostgreSQL│   │Redis │   │  Celery  │   │
│  │   Web   │───│ Database │   │      │───│  Worker  │   │
│  │  :8000  │   │  :5432   │   │:6379 │   │          │   │
│  └─────────┘   └──────────┘   └──────┘   └──────────┘   │
│       │                           │                       │
│  ┌─────────┐                 ┌──────────┐               │
│  │  Nginx  │                 │  Celery  │               │
│  │ (Future)│                 │   Beat   │               │
│  └─────────┘                 └──────────┘               │
└─────────────────────────────────────────────────────────────┘
```

### Individual Services

#### 1. **web** (Django Application)

- **Image**: Custom (built from Dockerfile)
- **Port**: 8000 (mapped to host)
- **Command**: `python manage.py runserver 0.0.0.0:8000`
- **Purpose**: Serves the Django REST API
- **Dependencies**: postgres, redis

**Key Features:**
- Auto-runs migrations on startup
- Hot-reload enabled (code changes reflect immediately)
- Connected to PostgreSQL and Redis

---

#### 2. **postgres** (Database)

- **Image**: postgres:15-alpine
- **Port**: 5432 (mapped to host)
- **Volume**: `postgres_data` (persists data)
- **Purpose**: Stores application data

**Default Credentials:**
- Database: `taskmanager_db`
- User: `postgres`
- Password: `postgres`

**Access from Host:**
```bash
psql -h localhost -U postgres -d taskmanager_db
```

---

#### 3. **redis** (Message Broker & Cache)

- **Image**: redis:7-alpine
- **Port**: 6379 (mapped to host)
- **Volume**: `redis_data` (persists data)
- **Purpose**: Celery message broker & caching

**Access from Host:**
```bash
redis-cli -h localhost -p 6379
# Try: PING (should return PONG)
```

---

#### 4. **celery-worker** (Async Task Processor)

- **Image**: Custom (same as web)
- **Command**: `celery -A taskmanager worker --loglevel=info`
- **Purpose**: Processes async tasks (emails, notifications)
- **Dependencies**: postgres, redis

**Monitor Tasks:**
```bash
# View worker logs
docker-compose logs -f celery-worker

# Check active tasks
docker-compose exec celery-worker celery -A taskmanager inspect active
```

---

#### 5. **celery-beat** (Scheduler)

- **Image**: Custom (same as web)
- **Command**: `celery -A taskmanager beat --loglevel=info`
- **Purpose**: Schedules periodic tasks
- **Dependencies**: postgres, redis

**Monitor Beat:**
```bash
# View beat scheduler logs
docker-compose logs -f celery-beat
```

---

## Environment Variables

### Configuration File: `.env`

Copy `.env.example` to `.env` and customize:

```bash
cp .env.example .env
```

### Key Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DEBUG` | `True` | Django debug mode |
| `SECRET_KEY` | dev-key | Django secret key (change in production!) |
| `DB_NAME` | `taskmanager_db` | PostgreSQL database name |
| `DB_USER` | `postgres` | PostgreSQL username |
| `DB_PASSWORD` | `postgres` | PostgreSQL password |
| `DB_HOST` | `postgres` | Database host (service name in Docker) |
| `EMAIL_HOST_USER` | - | Mailtrap username |
| `EMAIL_HOST_PASSWORD` | - | Mailtrap password |

### Docker vs Local Development

**Docker** (uses service names):
```env
DB_HOST=postgres
CELERY_BROKER_URL=redis://redis:6379/0
```

**Local** (uses localhost):
```env
DB_HOST=localhost
CELERY_BROKER_URL=redis://localhost:6379/0
```

---

## Common Commands

### Building & Starting

```bash
# Build images (first time or after Dockerfile changes)
docker-compose build

# Start services
docker-compose up

# Build and start in one command
docker-compose up --build

# Start in background (detached mode)
docker-compose up -d

# Start specific service only
docker-compose up web
```

### Stopping & Cleaning

```bash
# Stop services (containers remain)
docker-compose stop

# Stop and remove containers
docker-compose down

# Remove containers + volumes (DELETES DATA!)
docker-compose down -v

# Remove containers + images
docker-compose down --rmi all
```

### Viewing Logs

```bash
# View logs from all services
docker-compose logs

# Follow logs (like tail -f)
docker-compose logs -f

# Logs from specific service
docker-compose logs web
docker-compose logs celery-worker

# Last 100 lines
docker-compose logs --tail=100
```

### Executing Commands

```bash
# Run Django management commands
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py collectstatic

# Access Django shell
docker-compose exec web python manage.py shell

# Access PostgreSQL shell
docker-compose exec postgres psql -U postgres -d taskmanager_db

# Access Redis CLI
docker-compose exec redis redis-cli

# Run tests
docker-compose exec web pytest

# Run tests with coverage
docker-compose exec web pytest --cov=tasks --cov=accounts --cov=authentication
```

### Inspecting Services

```bash
# List running containers
docker-compose ps

# View service status
docker-compose top

# Inspect service configuration
docker-compose config

# Check resource usage
docker stats
```

### Database Operations

```bash
# Create database backup
docker-compose exec postgres pg_dump -U postgres taskmanager_db > backup.sql

# Restore database backup
docker-compose exec -T postgres psql -U postgres -d taskmanager_db < backup.sql

# Reset database (DELETES ALL DATA!)
docker-compose down -v
docker-compose up -d postgres
docker-compose exec web python manage.py migrate
```

---

## Development Workflow

### Daily Workflow

```bash
# Morning: Start services
docker-compose up -d

# Work on code (changes auto-reload)
# Edit Python files in your IDE

# View logs if needed
docker-compose logs -f web

# Evening: Stop services
docker-compose stop
```

### Making Code Changes

✅ **Auto-reload enabled**: Python code changes are detected automatically

**Files that auto-reload:**
- Python files (`.py`)
- Templates
- Most Django files

**Files that require restart:**
- `requirements.txt` (need to rebuild)
- `settings.py` changes to INSTALLED_APPS
- Dockerfile changes

**After adding new dependencies:**
```bash
docker-compose down
docker-compose up --build
```

### Running Tests in Docker

```bash
# Run all tests
docker-compose exec web pytest

# Run specific test file
docker-compose exec web pytest tasks/tests/test_models.py

# Run with coverage
docker-compose exec web pytest --cov=tasks --cov-report=html

# Run in watch mode (requires pytest-watch)
docker-compose exec web ptw
```

### Database Migrations

```bash
# Create new migrations
docker-compose exec web python manage.py makemigrations

# Apply migrations
docker-compose exec web python manage.py migrate

# Show migration status
docker-compose exec web python manage.py showmigrations

# Rollback migration
docker-compose exec web python manage.py migrate tasks 0001
```

---

## Troubleshooting

### Issue 1: Port Already in Use

**Error:**
```
ERROR: for postgres Cannot start service postgres: Ports are not available: listen tcp 0.0.0.0:5432: bind: address already in use
```

**Solution:**
```bash
# Find what's using the port
lsof -i :5432  # macOS/Linux
netstat -ano | findstr :5432  # Windows

# Stop the conflicting service or change port in docker-compose.yml
ports:
  - "5433:5432"  # Use different host port
```

---

### Issue 2: Permission Denied

**Error:**
```
PermissionError: [Errno 13] Permission denied
```

**Solution:**
```bash
# Fix file permissions
sudo chown -R $USER:$USER .

# Or run containers as current user
docker-compose exec -u $(id -u):$(id -g) web bash
```

---

### Issue 3: Database Connection Refused

**Error:**
```
django.db.utils.OperationalError: could not connect to server: Connection refused
```

**Solution:**
```bash
# 1. Check postgres is running
docker-compose ps

# 2. Wait for postgres to be ready (check health)
docker-compose logs postgres

# 3. Restart services in order
docker-compose down
docker-compose up -d postgres
# Wait 10 seconds
docker-compose up web
```

---

### Issue 4: Out of Disk Space

**Error:**
```
ERROR: No space left on device
```

**Solution:**
```bash
# Remove unused Docker resources
docker system prune -a --volumes

# View disk usage
docker system df
```

---

### Issue 5: Celery Not Processing Tasks

**Problem:** Tasks stuck in queue

**Solution:**
```bash
# 1. Check celery-worker is running
docker-compose ps celery-worker

# 2. Check worker logs
docker-compose logs celery-worker

# 3. Restart celery services
docker-compose restart celery-worker celery-beat

# 4. Purge task queue
docker-compose exec celery-worker celery -A taskmanager purge
```

---

### Issue 6: Hot Reload Not Working

**Problem:** Code changes not reflecting

**Solution:**
```bash
# 1. Check volumes are mounted
docker-compose config | grep volumes

# 2. Restart web service
docker-compose restart web

# 3. If still not working, rebuild
docker-compose up --build web
```

---

## Production Considerations

### For Production Deployment

**❌ DON'T use this docker-compose.yml directly in production!**

### Changes Needed for Production:

1. **Security**
   ```yaml
   # Use secure SECRET_KEY
   - SECRET_KEY=${SECRET_KEY}  # From secrets management

   # Disable DEBUG
   - DEBUG=False

   # Set allowed hosts
   - ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
   ```

2. **Web Server**
   - Use Gunicorn (already configured in Dockerfile)
   - Add Nginx reverse proxy
   - Enable HTTPS with SSL certificates

3. **Database**
   - Use managed database (AWS RDS, DigitalOcean Managed Database)
   - Or secure PostgreSQL with strong password
   - Regular backups

4. **Static Files**
   - Use Cloud Storage (AWS S3, DigitalOcean Spaces)
   - Or serve via CDN

5. **Environment Variables**
   - Use secrets management (AWS Secrets Manager, HashiCorp Vault)
   - Never commit `.env` to git

6. **Monitoring**
   - Add health checks
   - Logging (Sentry, ELK Stack)
   - Monitoring (Prometheus, Grafana)

7. **Scaling**
   - Use orchestration (Docker Swarm, Kubernetes)
   - Load balancing
   - Multiple workers

---

## Docker Cheat Sheet

### Quick Reference

```bash
# Build & Start
docker-compose up --build -d        # Build and start in background
docker-compose up web               # Start only web service
docker-compose restart web          # Restart service

# Stop & Clean
docker-compose stop                 # Stop services
docker-compose down                 # Stop and remove containers
docker-compose down -v              # Stop and remove volumes

# Logs & Debugging
docker-compose logs -f              # Follow all logs
docker-compose logs web --tail=50   # Last 50 lines from web
docker-compose exec web bash        # Shell into container

# Database
docker-compose exec postgres psql -U postgres  # PostgreSQL shell
docker-compose exec web python manage.py dbshell  # Django DB shell

# Django Management
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py shell

# Testing
docker-compose exec web pytest                    # Run tests
docker-compose exec web pytest --cov=tasks        # With coverage

# Cleanup
docker system prune -a              # Remove all unused resources
docker volume prune                 # Remove unused volumes
```

---

## Summary

Your Docker setup includes:

✅ **5 Services**: Django, PostgreSQL, Redis, Celery Worker, Celery Beat
✅ **Auto-reload**: Code changes reflect immediately
✅ **Data Persistence**: Volumes for database and Redis
✅ **Health Checks**: Services wait for dependencies
✅ **Easy Commands**: One command to start everything
✅ **Production-Ready**: Easy to adapt for deployment

**Next Steps:**
1. Copy `.env.example` to `.env`
2. Run `docker-compose up --build`
3. Create superuser: `docker-compose exec web python manage.py createsuperuser`
4. Access http://localhost:8000/admin/

**For questions or issues, check the [Troubleshooting](#troubleshooting) section.**