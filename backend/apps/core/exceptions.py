"""
Custom exception handler for ProjectMeats API.

Provides centralized error handling and logging for Django REST Framework.
"""
import logging
from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404
from django.db import DatabaseError

logger = logging.getLogger(__name__)


def exception_handler(exc, context):
    """
    Custom exception handler for DRF that logs errors and provides consistent responses.
    
    Args:
        exc: The exception being handled
        context: Context dictionary containing view, request, args, kwargs
    
    Returns:
        Response object with error details
    """
    # Call DRF's default exception handler first to get the standard error response
    response = drf_exception_handler(exc, context)

    # If DRF handled it, add extra logging and return
    if response is not None:
        # Log the error with context
        view = context.get('view', None)
        request = context.get('request', None)
        
        logger.error(
            f'API Error: {exc.__class__.__name__} - {str(exc)}',
            extra={
                'status_code': response.status_code,
                'view': view.__class__.__name__ if view else 'Unknown',
                'method': request.method if request else 'Unknown',
                'path': request.path if request else 'Unknown',
                'user': request.user.username if request and hasattr(request, 'user') and request.user.is_authenticated else 'Anonymous',
            },
            exc_info=True
        )
        return response

    # Handle Django validation errors
    if isinstance(exc, DjangoValidationError):
        logger.error(
            f'Django Validation Error: {str(exc)}',
            extra={
                'view': context.get('view').__class__.__name__ if context.get('view') else 'Unknown',
            },
            exc_info=True
        )
        return Response(
            {
                'error': 'Validation Error',
                'details': exc.messages if hasattr(exc, 'messages') else str(exc)
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # Handle 404 errors
    if isinstance(exc, Http404):
        logger.warning(
            f'404 Not Found: {str(exc)}',
            extra={
                'path': context.get('request').path if context.get('request') else 'Unknown',
            }
        )
        return Response(
            {'error': 'Not Found', 'details': str(exc)},
            status=status.HTTP_404_NOT_FOUND
        )

    # Handle database errors
    if isinstance(exc, DatabaseError):
        logger.critical(
            f'Database Error: {str(exc)}',
            extra={
                'view': context.get('view').__class__.__name__ if context.get('view') else 'Unknown',
            },
            exc_info=True
        )
        return Response(
            {
                'error': 'Database Error',
                'details': 'A database error occurred. Please try again later.'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    # Handle any other unhandled exceptions
    logger.error(
        f'Unhandled Exception: {exc.__class__.__name__} - {str(exc)}',
        extra={
            'view': context.get('view').__class__.__name__ if context.get('view') else 'Unknown',
            'request_method': context.get('request').method if context.get('request') else 'Unknown',
            'request_path': context.get('request').path if context.get('request') else 'Unknown',
        },
        exc_info=True
    )
    
    return Response(
        {
            'error': 'Internal Server Error',
            'details': 'An unexpected error occurred. Please try again later.'
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
