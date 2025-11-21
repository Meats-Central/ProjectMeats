# Global Exception Handling and Enhanced Logging

This document describes the global exception handling and logging improvements implemented to fix 500 Internal Server Errors in the ProjectMeats API.

## Overview

A custom Django REST Framework exception handler has been implemented to provide centralized error handling, comprehensive logging, and consistent error responses across all API endpoints.

## Implementation Details

### 1. Custom Exception Handler

**Location:** `backend/apps/core/exceptions.py`

The custom exception handler:
- Intercepts all exceptions raised during request processing
- Logs errors with full context (view, request method, path, user, timestamp)
- Returns consistent error responses with appropriate HTTP status codes
- Handles multiple exception types with appropriate responses:
  - `DRFValidationError` → 400 Bad Request (logged as ERROR)
  - `DjangoValidationError` → 400 Bad Request (logged as ERROR)
  - `Http404` → 404 Not Found (logged as WARNING)
  - `DatabaseError` → 500 Internal Server Error (logged as CRITICAL)
  - Generic exceptions → 500 Internal Server Error (logged as ERROR)

### 2. Settings Configuration

**Location:** `backend/projectmeats/settings/base.py`

Changes made:
```python
REST_FRAMEWORK = {
    # ... other settings ...
    "EXCEPTION_HANDLER": "apps.core.exceptions.exception_handler",
}

LOGGING = {
    # ... other settings ...
    "handlers": {
        # ... other handlers ...
        "debug_file": {
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "logs" / "debug.log",
            "formatter": "verbose",
            "level": "DEBUG",
        },
    },
    "loggers": {
        # All app view loggers now use debug_file handler
        "apps.suppliers.views": {
            "handlers": ["console", "debug_file"],
            "level": "DEBUG",
        },
        # ... similar for other apps ...
        "apps.core.exceptions": {
            "handlers": ["console", "debug_file"],
            "level": "DEBUG",
        },
    },
}
```

### 3. Logs Directory

**Location:** `backend/logs/`

- Created directory with `.gitkeep` file to ensure it's tracked in git
- Log files (`django.log`, `debug.log`) are written here
- Log files are excluded from git via `.gitignore`

### 4. Health Check Endpoints

Health check endpoints already existed and were verified working:

- **Basic Health Check:** `GET /api/v1/health/`
  - Returns database status and basic system info
  - Returns 200 when healthy, 503 when unhealthy

- **Detailed Health Check:** `GET /api/v1/health/detailed/`
  - Returns comprehensive system health including memory, disk, CPU
  - Includes database connectivity check
  - Returns 200 when healthy, 503 when unhealthy

## Error Response Format

All errors now return consistent JSON responses:

### Validation Errors (400)
```json
{
  "field_name": ["Error message"]
}
```

### Custom Handled Errors (400, 404, 500)
```json
{
  "error": "Error Type",
  "details": "Detailed error message"
}
```

## Logging Format

All errors are logged with the following context:
- Log level (ERROR, WARNING, CRITICAL)
- Timestamp
- Exception type and message
- View name
- Request method
- Request path
- User (username or 'Anonymous')
- Full stack trace

Example log entry:
```
ERROR 2025-10-09 15:32:43,770 exceptions 3602 140619271577728 API Error: ValidationError - {'name': ErrorDetail(string='This field is required', code='invalid')}
```

## Testing

The exception handler has been tested with:
- DRF ValidationError
- Django ValidationError
- DatabaseError
- Generic exceptions

All supplier endpoint tests pass successfully.

## Benefits

1. **Better Debugging:** All errors are logged with full context, making it easier to diagnose issues
2. **Consistent API:** Clients receive predictable error responses
3. **Security:** Sensitive error details are logged but not exposed to clients
4. **Monitoring:** Errors can be tracked and analyzed from log files
5. **Production Ready:** Different log levels help prioritize issues (CRITICAL vs WARNING)

## Dependencies

- Django REST Framework (already installed)
- psycopg2-binary==2.9.9 (for PostgreSQL support with django-tenants)

## Usage

No code changes required in views. The exception handler automatically catches and processes all exceptions:

```python
# Before - manual error handling in each view
def create(self, request, *args, **kwargs):
    try:
        return super().create(request, *args, **kwargs)
    except Exception as e:
        logger.error(f"Error: {e}")
        return Response({"error": str(e)}, status=500)

# After - automatic handling by global exception handler
def create(self, request, *args, **kwargs):
    return super().create(request, *args, **kwargs)
    # All errors automatically logged and handled
```

## Monitoring

To monitor errors in production:

1. **Check logs:**
   ```bash
   tail -f backend/logs/debug.log
   ```

2. **Filter critical errors:**
   ```bash
   grep CRITICAL backend/logs/debug.log
   ```

3. **Monitor health:**
   ```bash
   curl http://localhost:8000/api/v1/health/
   ```

## Future Enhancements

Potential improvements:
1. Integrate with error tracking service (e.g., Sentry)
2. Add structured logging (JSON format)
3. Implement error alerting for CRITICAL errors
4. Add metrics tracking for error rates
5. Create dashboard for error monitoring
