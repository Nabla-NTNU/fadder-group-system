"""
Production settings for fadder-site
"""

from os import environ as env
import pymysql
from .base import *

pymysql.install_as_MySQLdb()

ALLOWED_HOSTS = ['fadder.nabla.no', '127.0.0.1']

DEBUG = bool(env.get('DEBUG', False))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': env.get('MYSQL_DATABASE', 'fadder'),
        'USER': env.get('MYSQL_USER', 'fadder'),
        'PASSWORD': env.get('MYSQL_USER_PASSWORD', ''),
    }
}
