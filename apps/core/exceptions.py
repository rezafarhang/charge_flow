from rest_framework.views import exception_handler as drf_exception_handler
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    response = drf_exception_handler(exc, context)

    if response is not None:
        logger.error(
            f"API Exception: {exc.__class__.__name__}",
            extra={
                'exception': str(exc),
                'view': context.get('view').__class__.__name__ if context.get('view') else None,
                'request': context.get('request').path if context.get('request') else None,
            }
        )

    return response
