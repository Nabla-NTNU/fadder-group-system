"""
Production settings for fadder-site
"""

from os import environ as env
from .base import *


ALLOWED_HOSTS = ["fadder.nabla.no", "127.0.0.1"]

DEBUG = bool(env.get("DEBUG", False))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.get("SECRET_KEY")

GOOGLE_RECAPTCHA_SECRET_KEY = env.get("GOOGLE_RECAPTCHA_SECRET_KEY")
GOOGLE_RECAPTCHA_SITE_KEY = env.get("GOOGLE_RECAPTCHA_SITE_KEY")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": env.get("MYSQL_DATABASE", "fadder"),
        "USER": env.get("MYSQL_USER", "fadder"),
        "PASSWORD": env.get("MYSQL_USER_PASSWORD", ""),
    }
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"timestamp": {"format": "%(asctime)s %(message)s"}},
    "handlers": {
        "file": {
            "level": "ERROR",
            "class": "logging.FileHandler",
            "filename": env.get("DJANGO_LOG_PATH", "/var/log/django/fadder/error.log"),
            "formatter": "timestamp",
        },
    },
    "loggers": {"django": {"handlers": ["file"], "level": "ERROR", "propagate": True}},
}
