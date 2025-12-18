# Charge Flow - Django REST Framework Project

A Django REST Framework project following enterprise-level backend development standards with PostgreSQL database, Redis caching, and Celery task queue.

## Tech Stack

- **Framework**: Django 4.2+ with Django REST Framework
- **Database**: PostgreSQL 15
- **Cache & Message Broker**: Redis 7
- **Task Queue**: Celery
- **API Documentation**: drf-spectacular (OpenAPI)
- **Authentication**: JWT (djangorestframework-simplejwt)
- **Python**: 3.11+

## Project Structure

```
charge_flow/
├── apps/
│   ├── core/              # Shared utilities, decorators, base classes
│   ├── users/             # User management and authentication
│   ├── throttling/        # Rate limiting and throttle classes
│   └── transaction/       # Transaction management
├── config/
│   ├── settings/          # Split settings by concern
│   │   ├── base.py
│   │   ├── local.py
│   │   ├── production.py
│   │   ├── settings_database.py
│   │   └── settings_rest.py
│   ├── urls.py
│   └── wsgi.py
├── requirements/          # base.txt, local.txt, production.txt
├── docker/               # Docker configurations
├── Dockerfile
├── docker-compose.yml
└── manage.py
```

## Setup Instructions

### Prerequisites

- Python 3.11+
- PostgreSQL 15
- Redis 7
- Docker & Docker Compose (for containerized setup)

### Local Development Setup

1. **Clone the repository**
   ```bash
   cd charge_flow
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements/local.txt
   ```

4. **Create .env file**
   ```bash
   cp .env.example .env
   # Edit .env with your local settings
   ```

5. **Create database**
   ```bash
   createdb charge_flow
   ```

6. **Run migrations**
   ```bash
   python manage.py migrate
   ```

7. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

8. **Run development server**
   ```bash
   python manage.py runserver
   ```

### Docker Setup

1. **Create .env file**
   ```bash
   cp .env.example .env
   ```

2. **Build and start containers**
   ```bash
   docker-compose up --build
   ```

3. **Run migrations**
   ```bash
   docker-compose exec web python manage.py migrate
   ```

4. **Create superuser**
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

5. **Access the application**
   - API: http://localhost:8000
   - Admin: http://localhost:8000/admin/
   - API Docs: http://localhost:8000/api/docs/

## API Structure

- **Base URL**: `/api/v1/`
- **Authentication**: JWT Bearer Token
- **Documentation**: OpenAPI/Swagger at `/api/docs/`

### Example Endpoints

```
POST   /api/v1/users/register/          # User registration
POST   /api/v1/users/login/             # User login
POST   /api/v1/users/token/refresh/     # Refresh JWT token
GET    /api/v1/users/me/                # Get current user
```

## Development Standards

### Code Style
- Line length: 88 characters (Black default)
- Import ordering: isort with Black compatibility
- Linting: flake8
- Docstrings: Google style

### Testing
- Framework: Python's built-in unittest
- Minimum coverage: 80%
- Run tests: `python manage.py test`

### Code Organization
- **Serializers**: For serialization and basic validation only
- **Managers**: All complex validation and business logic
- **Views**: Generic APIViews for flexibility
- **Constants**: All constants in `consts.py` with `status_decorator`

### Error Handling
Use status_decorator pattern for error constants:

```python
from apps.core.decorators import status_decorator

@status_decorator
class MyError:
    code = 100
    message = 'Error message: {}'

# Usage
raise exceptions.ValidationError(
    MyError().get_status(dynamic_value)
)
```

## Running Celery

### Local Development
```bash
# Worker
celery -A config worker --loglevel=info

# Beat scheduler
celery -A config beat --loglevel=info
```

### Docker
Celery workers and beat scheduler are automatically started with docker-compose.

## Database Management

### Create migrations
```bash
python manage.py makemigrations
```

### Apply migrations
```bash
python manage.py migrate
```

### Reset database
```bash
python manage.py flush
```

## Useful Commands

### Collect static files
```bash
python manage.py collectstatic
```

### Create app
```bash
python manage.py startapp app_name apps/app_name
```

### Django shell
```bash
python manage.py shell
```

### Check for issues
```bash
python manage.py check
```

## Code Quality Tools

### Format code with Black
```bash
black .
```

### Sort imports with isort
```bash
isort .
```

### Lint with flake8
```bash
flake8 .
```

## Environment Variables

Key environment variables (see `.env.example` for full list):

- `DJANGO_ENV`: Environment (local/production)
- `SECRET_KEY`: Django secret key
- `DEBUG`: Debug mode (True/False)
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`: Database credentials
- `REDIS_URL`: Redis connection URL
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts

## Security Notes

- Never commit `.env` file
- Always use environment variables for secrets
- Keep `DEBUG=False` in production
- Use HTTPS in production
- Regular security updates for dependencies

## Contributing

1. Create feature branch from `main`
2. Write tests for new features
3. Ensure code passes all quality checks
4. Submit pull request with clear description

## License

[Your License Here]

## Support

For issues and questions, please contact the development team.
