"""
Development settings for fadder-site
"""

from .base import *

ALLOWED_HOSTS = ["fadder.nabla.no", "localhost", "127.0.0.1"]

DEBUG = True

SECRET_KEY = "not_so_secret_devel_key"

# GOOGLE_RECAPTCHA_SECRET_KEY  = os.environ.get("GOOGLE_RECAPTCHA_SECRET_KEY", "not_secret_fallback_devel_key")
# GOOGLE_RECAPTCHA_SITE_KEY = os.environ.get("GOOGLE_RECAPTCHA_SITE_KEY", "not_secret_fallback_devel_key")

# Local dev test keys given in https://developers.google.com/recaptcha/docs/faq
GOOGLE_RECAPTCHA_SITE_KEY = "6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI"
GOOGLE_RECAPTCHA_SECRET_KEY = "6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe"


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
