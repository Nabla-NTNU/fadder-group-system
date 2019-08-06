"""
Development settings for fadder-site
"""

from .base import *

ALLOWED_HOSTS = ["fadder.nabla.no", "localhost", "127.0.0.1"]

DEBUG = True


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
