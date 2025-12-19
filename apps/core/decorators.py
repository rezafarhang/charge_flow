def status_decorator(cls):
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
