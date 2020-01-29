"""
Development settings for fadder-site
"""

from .base import *

ALLOWED_HOSTS = ["fadder.nabla.no", "localhost", "127.0.0.1"]

DEBUG = True

SECRET_KEY = "not_so_secret_devel_key"

GOOGLE_RECAPTCHA_SECRET_KEY  = os.environ.get("GOOGLE_RECAPTCHA_SECRET_KEY", "not_secret_fallback_devel_key")
GOOGLE_RECAPTCHA_SITE_KEY = os.environ.get("GOOGLE_RECAPTCHA_SITE_KEY", "not_secret_fallback_devel_key")

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
