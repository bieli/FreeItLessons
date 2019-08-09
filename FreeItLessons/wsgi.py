"""
WSGI config for FreeItLessons project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/howto/deployment/wsgi/
"""
import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'FreeItLessons.settings'

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
