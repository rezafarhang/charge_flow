DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]', "0.0.0.0"]

SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# CORS - Allow all origins in local development
CORS_ALLOW_ALL_ORIGINS = True