"""
Core decorators for the project.
"""


def status_decorator(cls):
    """
    Decorator for error constant classes that adds get_status method.

    Usage:
        @status_decorator
        class MyError:
            code = 1
            message = 'Error: {}'

    The get_status method will format the message with provided arguments
    and return a dict with code and message.
    """
    def get_status(self, *args, **kwargs):
        try:
            message = self.message.format(*args, **kwargs)
        except Exception:
            message = self.message
        return {
            "code": getattr(self, "code"),
            "message": message
        }

    setattr(cls, "get_status", get_status)
    return cls
