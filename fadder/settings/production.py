"""
Production settings for fadder-site
"""

from os import environ as env
import pymysql
from .base import *

pymysql.install_as_MySQLdb()

ALLOWED_HOSTS = ['fadder.nabla.no', '127.0.0.1']

DEBUG = bool(env.get('DEBUG', False))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY")

GOOGLE_RECAPTCHA_SECRET_KEY  = os.environ.get("GOOGLE_RECAPTCHA_SECRET_KEY")
GOOGLE_RECAPTCHA_SITE_KEY = os.environ.get("GOOGLE_RECAPTCHA_SITE_KEY")

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': env.get('MYSQL_DATABASE', 'fadder'),
        'USER': env.get('MYSQL_USER', 'fadder'),
        'PASSWORD': env.get('MYSQL_USER_PASSWORD', ''),
    }
}
