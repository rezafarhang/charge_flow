from .base import *
from .settings_database import *
from .settings_rest import *

# Load environment-specific settings
environment = os.environ.get('DJANGO_ENV', 'local')

if environment == 'production':
    from .production import *
else:
    from .local import *
