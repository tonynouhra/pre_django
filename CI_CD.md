# CI/CD Pipeline Documentation

## Table of Contents

1. [Overview](#overview)
2. [Pipeline Architecture](#pipeline-architecture)
3. [GitHub Actions Workflow](#github-actions-workflow)
4. [Code Quality Tools](#code-quality-tools)
5. [Running Checks Locally](#running-checks-locally)
6. [Understanding the Pipeline](#understanding-the-pipeline)
7. [Troubleshooting](#troubleshooting)
8. [Future Enhancements](#future-enhancements)

---

## Overview

This project uses **GitHub Actions** for continuous integration and continuous deployment (CI/CD). Every push and pull request triggers automated checks to ensure code quality, security, and functionality.

### What Gets Checked?

✅ **Code Quality** - Black, isort, flake8, pylint
✅ **Security** - Vulnerability scanning with Safety
✅ **Tests** - 113+ tests with 90% coverage
✅ **Docker** - Image builds and compose validation
✅ **Database Migrations** - Automatic migration checks

### Workflow Triggers

The CI/CD pipeline runs on:
- **Push** to `main` or `develop` branches
- **Pull requests** targeting `main` or `develop` branches

---

## Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   GitHub Push / Pull Request                 │
└─────────────────────────┬───────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Code Quality │  │   Security   │  │   Run Tests  │
│    Checks    │  │     Scan     │  │ with Coverage│
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                 │
       └─────────────────┼─────────────────┘
                         │
                         ▼
                 ┌──────────────┐
                 │ Build Docker │
                 │    Image     │
                 └──────┬───────┘
                        │
                        ▼
                 ┌──────────────┐
                 │   Deploy     │
                 │ (Placeholder)│
                 └──────────────┘
```

---

## GitHub Actions Workflow

The workflow is defined in `.github/workflows/ci.yml` and consists of 5 jobs:

### Job 1: Code Quality

**Purpose**: Ensure code follows Python best practices and style guidelines

**Tools Used**:
- **Black** - Code formatter (PEP 8 compliant)
- **isort** - Import statement sorter
- **flake8** - Style guide enforcement
- **pylint** - Code analysis
- **mypy** - Static type checker

**What It Checks**:
- Code formatting consistency
- Import statement organization
- PEP 8 compliance
- Code complexity
- Type hints

**Example Output**:
```
✓ Black formatting check passed
✓ isort import sorting passed
✓ flake8 found 0 errors
```

---

### Job 2: Security Scan

**Purpose**: Identify known security vulnerabilities in dependencies

**Tools Used**:
- **Safety** - Checks Python dependencies against known vulnerability database

**What It Checks**:
- Vulnerable package versions
- Known CVEs in dependencies
- Outdated security patches

**Example Output**:
```
Scanning 84 packages...
✓ No known security vulnerabilities found
```

---

### Job 3: Run Tests

**Purpose**: Execute full test suite with code coverage

**Infrastructure**:
- **PostgreSQL 15** - Test database (service container)
- **Redis 7** - Cache and message broker (service container)

**What It Does**:
1. Sets up Python 3.11 environment
2. Installs project dependencies
3. Runs database migrations
4. Executes 113+ tests with pytest
5. Generates coverage report (90%+)
6. Uploads coverage to Codecov

**Commands Executed**:
```bash
python manage.py migrate --no-input
pytest --cov=tasks --cov=accounts --cov=authentication \
       --cov-report=xml --cov-report=term-missing \
       --cov-fail-under=80
```

**Example Output**:
```
==================== test session starts ====================
collected 113 items

tasks/tests/test_models.py .................... [ 42%]
tasks/tests/test_views.py ..................... [ 77%]
tasks/tests/test_serializers.py ........       [ 88%]
authentication/tests/test_views.py ..........   [100%]

---------- coverage: platform linux, python 3.11 -----------
Name                              Stmts   Miss  Cover
-----------------------------------------------------
tasks/models.py                     158     12    92%
tasks/views.py                      142      8    94%
tasks/serializers.py                 87      5    94%
authentication/views.py              92      7    92%
-----------------------------------------------------
TOTAL                               479     32    93%

==================== 113 passed in 12.34s ===================
```

---

### Job 4: Build Docker Image

**Purpose**: Verify Docker image builds successfully

**What It Does**:
- Builds Docker image using `Dockerfile`
- Validates `docker-compose.yml` configuration
- Uses Docker layer caching for faster builds
- Only runs on `main` branch pushes

**Technologies**:
- Docker Buildx for multi-platform builds
- GitHub Actions cache for Docker layers

**Example Output**:
```
Building Docker image: taskmanager:abc123
✓ Image built successfully
✓ docker-compose.yml configuration valid
```

---

### Job 5: Deploy

**Purpose**: Placeholder for future deployment automation

**Current Status**: Not yet implemented

**Future Deployment Options**:
- AWS Elastic Beanstalk
- DigitalOcean App Platform
- Heroku
- Kubernetes cluster
- AWS ECS/Fargate

---

## Code Quality Tools

### 1. Black - Code Formatter

**Configuration**: `pyproject.toml`

```toml
[tool.black]
line-length = 127
target-version = ['py311']
```

**Purpose**: Automatically format Python code to PEP 8 standards

**Run Locally**:
```bash
# Check formatting
black --check .

# Auto-fix formatting
black .
```

---

### 2. isort - Import Sorter

**Configuration**: `pyproject.toml`

```toml
[tool.isort]
profile = "black"
line_length = 127
known_django = ["django"]
known_drf = ["rest_framework"]
```

**Purpose**: Organize import statements consistently

**Run Locally**:
```bash
# Check import sorting
isort --check-only .

# Auto-fix import sorting
isort .
```

---

### 3. flake8 - Linter

**Configuration**: `.flake8`

```ini
[flake8]
max-line-length = 127
max-complexity = 10
exclude = migrations,venv,__pycache__
```

**Purpose**: Enforce PEP 8 style guide and find code issues

**Run Locally**:
```bash
# Run flake8
flake8 .

# Check specific files
flake8 tasks/models.py
```

---

### 4. pytest - Testing Framework

**Configuration**: `pyproject.toml` and `pytest.ini`

**Purpose**: Run tests and generate coverage reports

**Run Locally**:
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=tasks --cov=accounts --cov=authentication

# Run specific test file
pytest tasks/tests/test_models.py

# Run tests matching pattern
pytest -k "test_task_creation"
```

---

## Running Checks Locally

### Before Committing Code

Run these commands to ensure your code will pass CI checks:

```bash
# 1. Format code
black .
isort .

# 2. Lint code
flake8 .

# 3. Run tests
pytest

# 4. Check coverage
pytest --cov=tasks --cov=accounts --cov=authentication --cov-fail-under=80

# 5. Test Docker build
docker-compose build

# 6. Test Docker services
docker-compose up -d
docker-compose exec web python manage.py check
docker-compose down
```

### One-Line Pre-Commit Check

```bash
black . && isort . && flake8 . && pytest --cov=tasks --cov=accounts --cov=authentication --cov-fail-under=80
```

If all commands succeed, your code is ready to commit!

---

## Understanding the Pipeline

### When Does It Run?

**On Push**:
```bash
git push origin main        # Triggers full pipeline
git push origin develop     # Triggers full pipeline
git push origin feature/x   # Does NOT trigger (only main/develop)
```

**On Pull Request**:
```bash
# Opening or updating a PR to main or develop triggers the pipeline
gh pr create --base main --head feature/new-feature
```

### Viewing Pipeline Results

**GitHub UI**:
1. Go to your repository on GitHub
2. Click the "Actions" tab
3. Select a workflow run
4. View individual job logs

**Pull Request Checks**:
- PR page shows status of all checks
- Green checkmark = All checks passed
- Red X = Some checks failed
- Click "Details" to view logs

### Pipeline Status Badge

Add to your README.md:
```markdown
![CI](https://github.com/username/repo/workflows/CI%2FCD%20Pipeline/badge.svg)
```

---

## Troubleshooting

### Common Issues

#### 1. Black Formatting Failures

**Error**:
```
would reformat tasks/views.py
Oh no! 💥 💔 💥
1 file would be reformatted
```

**Fix**:
```bash
# Auto-fix formatting
black .

# Then commit the changes
git add .
git commit -m "Fix code formatting with Black"
git push
```

---

#### 2. Import Sorting Failures

**Error**:
```
ERROR: Imports are incorrectly sorted and/or formatted.
```

**Fix**:
```bash
# Auto-fix imports
isort .

# Then commit
git add .
git commit -m "Fix import sorting"
git push
```

---

#### 3. Test Failures

**Error**:
```
FAILED tasks/tests/test_models.py::TestTaskModel::test_task_creation
```

**Debug**:
```bash
# Run the failing test locally
pytest tasks/tests/test_models.py::TestTaskModel::test_task_creation -v

# Run with detailed output
pytest tasks/tests/test_models.py::TestTaskModel::test_task_creation -vv -s

# Run in Docker (matches CI environment)
docker-compose exec web pytest tasks/tests/test_models.py::TestTaskModel::test_task_creation
```

---

#### 4. Coverage Below Threshold

**Error**:
```
FAILED - coverage is 78%, required is 80%
```

**Fix**:
```bash
# Identify uncovered lines
pytest --cov=tasks --cov-report=term-missing

# Write tests for uncovered code
# Example output shows:
# tasks/models.py    92%   45-48, 67-70

# Add tests for lines 45-48 and 67-70
```

---

#### 5. Docker Build Failures

**Error**:
```
ERROR: failed to solve: process "/bin/sh -c pip install -r requirements.txt" did not complete successfully
```

**Debug Locally**:
```bash
# Build Docker image
docker build -t taskmanager:test .

# If it fails, check requirements.txt
cat requirements.txt

# Try building without cache
docker build --no-cache -t taskmanager:test .
```

---

#### 6. Migration Failures

**Error**:
```
django.db.migrations.exceptions.InconsistentMigrationHistory
```

**Fix**:
```bash
# Check for migration conflicts
python manage.py showmigrations

# If conflicts exist, create a merge migration
python manage.py makemigrations --merge

# Commit the merge migration
git add */migrations/*
git commit -m "Resolve migration conflicts"
git push
```

---

## Environment Variables in CI

The CI pipeline uses these environment variables:

```yaml
DEBUG: 'True'
SECRET_KEY: 'test-secret-key-for-ci-only'
DB_NAME: 'test_taskmanager_db'
DB_USER: 'postgres'
DB_PASSWORD: 'postgres'
DB_HOST: 'localhost'
DB_PORT: '5432'
CELERY_BROKER_URL: 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND: 'redis://localhost:6379/0'
```

**Note**: These are test values only. Production values are stored as GitHub Secrets.

---

## Adding GitHub Secrets

For deployment, add secrets to your repository:

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Add secrets:
   - `DJANGO_SECRET_KEY` - Production secret key
   - `DATABASE_URL` - Production database URL
   - `REDIS_URL` - Production Redis URL
   - `DEPLOY_SSH_KEY` - SSH key for deployment

**Access secrets in workflow**:
```yaml
env:
  SECRET_KEY: ${{ secrets.DJANGO_SECRET_KEY }}
```

---

## Future Enhancements

### Planned CI/CD Improvements

1. **Automated Deployment**
   - Deploy to staging on `develop` branch
   - Deploy to production on `main` branch
   - Rollback on deployment failure

2. **Additional Checks**
   - Dependency vulnerability scanning (Dependabot)
   - License compliance checking
   - Performance regression testing
   - Database migration safety checks

3. **Notifications**
   - Slack/Discord notifications on build status
   - Email alerts on failures
   - GitHub status checks on PRs

4. **Caching Improvements**
   - Cache pip dependencies
   - Cache Docker layers
   - Cache test database

5. **Parallel Testing**
   - Split tests across multiple workers
   - Reduce CI run time from 5 minutes to 2 minutes

6. **Release Automation**
   - Automatic versioning (semantic versioning)
   - Changelog generation
   - GitHub release creation
   - Docker image tagging and pushing

---

## Best Practices

### For Developers

1. **Run checks before pushing**:
   ```bash
   black . && isort . && flake8 . && pytest
   ```

2. **Keep tests fast** - CI runs on every push

3. **Write meaningful commit messages** - Helps debug CI failures

4. **Fix CI failures immediately** - Don't merge broken code

5. **Review coverage reports** - Aim for 80%+ coverage

### For Reviewers

1. **Check CI status** - Don't approve PRs with failing checks

2. **Review coverage changes** - Ensure new code is tested

3. **Watch for security issues** - Safety scan results matter

4. **Verify Docker builds** - Production image must build

---

## Monitoring CI/CD

### Metrics to Track

- **Build Success Rate**: % of successful builds
- **Build Duration**: Time to complete pipeline
- **Test Coverage**: % of code covered by tests
- **Deployment Frequency**: How often code is deployed

### GitHub Insights

View CI/CD metrics:
1. Go to **Insights** → **Actions**
2. See workflow run statistics
3. Analyze failure patterns
4. Optimize slow steps

---

## Summary

Your CI/CD pipeline ensures:

✅ **Code Quality** - Automated formatting and linting
✅ **Security** - Vulnerability scanning
✅ **Reliability** - 113+ tests with 90% coverage
✅ **Docker-Ready** - Validated containerization
✅ **Fast Feedback** - Results in ~5 minutes

**Every commit is automatically tested and validated before deployment.**

---

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [pytest Documentation](https://docs.pytest.org/)
- [Black Documentation](https://black.readthedocs.io/)
- [flake8 Documentation](https://flake8.pycqa.org/)
- [Docker CI Best Practices](https://docs.docker.com/build/ci/)

---

**Questions or Issues?**

If you encounter CI/CD problems:
1. Check this documentation
2. Review GitHub Actions logs
3. Run checks locally first
4. Open an issue with workflow run link