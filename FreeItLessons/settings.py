"""
Django settings for FreeItLessons project.

Every deployment specific value can be overridden with an environment
variable (see README.md, section "Configuration").

https://docs.djangoproject.com/en/stable/topics/settings/
https://docs.djangoproject.com/en/stable/ref/settings/
"""
import os
import sys
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured


def env_bool(name, default):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in ('1', 'true', 'yes', 'on')


def env_list(name, default):
    value = os.environ.get(name)
    if value is None:
        return default
    return [item.strip() for item in value.split(',') if item.strip()]


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env_bool('DJANGO_DEBUG', False)

# SECURITY WARNING: keep the secret key used in production secret!
# (the key formerly committed to this repository is public - never reuse it)
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', '')
if not SECRET_KEY:
    if not DEBUG:
        raise ImproperlyConfigured('Set the DJANGO_SECRET_KEY environment variable '
                                   '(or DJANGO_DEBUG=1 for local development).')
    SECRET_KEY = 'django-insecure-local-development-only'

ALLOWED_HOSTS = env_list('DJANGO_ALLOWED_HOSTS', ['127.0.0.1', 'localhost'])
CSRF_TRUSTED_ORIGINS = env_list('DJANGO_CSRF_TRUSTED_ORIGINS', [])

# HTTPS hardening - enable when served over TLS (see README "Configuration")
SECURE_SSL_REDIRECT = env_bool('DJANGO_SECURE_SSL_REDIRECT', False)
SESSION_COOKIE_SECURE = env_bool('DJANGO_SECURE_COOKIES', False)
CSRF_COOKIE_SECURE = SESSION_COOKIE_SECURE
SECURE_HSTS_SECONDS = int(os.environ.get('DJANGO_SECURE_HSTS_SECONDS', '0'))
SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool('DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS', False)
if env_bool('DJANGO_BEHIND_TLS_PROXY', False):
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_HTTPONLY = True
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = 'same-origin'

# The only login page of the site is the admin one (students log in there too).
LOGIN_URL = '/admin/login/'

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'bootstrap3',
    'mainapp',
    'adminsortable2',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'FreeItLessons.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'FreeItLessons.wsgi.application'


# Database
# https://docs.djangoproject.com/en/stable/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.environ.get('DJANGO_DB_PATH', str(BASE_DIR / 'db.sqlite3')),
    }
}

# Primary keys of the existing schema are 32 bit integers.
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# Password validation
# https://docs.djangoproject.com/en/stable/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/stable/topics/i18n/

LANGUAGE_CODE = 'pl-pl'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/stable/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = os.environ.get('DJANGO_STATIC_ROOT', str(BASE_DIR / 'staticfiles'))

# NOTE: the legacy STATICFILES_DIRS = (BASE_DIR / 'mainapp',) published the
# application's source code and templates under /static/ - removed. All assets
# live in mainapp/static/ and are found by the app directories finder.

STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
    },
}

# Serve static files straight from the app directories when DEBUG is on
# (same behaviour as `runserver`), and from STATIC_ROOT otherwise.
WHITENOISE_USE_FINDERS = DEBUG

SITE_ID = 1

ADMINS = (
    ('Pomoc mentorska', 'contact@yourdomain.com'),
)

COMPANY = {
    'NAME': "my company",
    'ADDRESS': "26 streets from here th there",
    'ZIP': "1234",
    'CITY': "Paris",
    'LAT': 48.81484460000001,
    'LNG': 2.0523723999999675,
    'PHONE': "+336 1234 5678",
    'EMAIL': 'contact@yourdomain.com',
    'FACEBOOK': "https://www.facebook.com/highfeature",
    'LINKEDIN': "http://www.linkedin.com/in/ivarsalain",
    'TWITTER': "https://twitter.com/HighFeature",
    'GOOGLEPLUS': "https://twitter.com/HighFeature",
}

CONTACT_FORM_SUBJECT_TEMPLATE_NAME = 'email_subject.txt'
CONTACT_FORM_MESSAGE_TEMPLATE_NAME = 'email_message.txt'

COMPANY_INFOS = {
    'NAME': "my company",
    'ADDRESS': "26 streets from here th there",
    'ZIP': "1234",
    'CITY': "Maybe-there",
    'LAT': 48.81484460000001,
    'LNG': 2.0523723999999675,
    'PHONE': "+336 1234 5678",
    'EMAIL': 'contact@mycompany.com',
    'FACEBOOK': "http://fr-fr.facebook.com/people/Maybe-there",
    'LINKEDIN': "http://www.linkedin.com/in/Maybe-there",
    'TWITTER': "http://twitter.com/Maybe-there",
    'GOOGLEPLUS': "https://plus.google.com/Maybe-there/posts",
}


CRISPY_TEMPLATE_PACK = 'bootstrap3'

USE_RECAPTCHA = False
RECAPTCHA_PUBLIC_KEY = 'your reCapcha public key'
RECAPTCHA_PRIVATE_KEY = 'your reCapcha private key'

EMAIL_HOST = os.environ.get('DJANGO_EMAIL_HOST', '')
EMAIL_PORT = int(os.environ.get('DJANGO_EMAIL_PORT', '25'))
EMAIL_HOST_USER = os.environ.get('DJANGO_EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('DJANGO_EMAIL_HOST_PASSWORD', '')

# Interpreter used to run students' solutions (defaults to the one running Django).
PYTHON_EXEC = os.environ.get('PYTHON_EXEC', sys.executable)

TEMP_SOLUTION_CODE_BLOCK = os.environ.get('TEMP_SOLUTION_CODE_BLOCK', '/tmp/')

# Limits of a single run of a student's program (mainapp/sandbox.py)
CODE_RUN_TIMEOUT_SECONDS = int(os.environ.get('CODE_RUN_TIMEOUT_SECONDS', '5'))
CODE_RUN_MEMORY_MB = int(os.environ.get('CODE_RUN_MEMORY_MB', '256'))
CODE_RUN_OUTPUT_KB = int(os.environ.get('CODE_RUN_OUTPUT_KB', '256'))

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {'console': {'class': 'logging.StreamHandler'}},
    'loggers': {'mainapp': {'handlers': ['console'], 'level': os.environ.get('DJANGO_LOG_LEVEL', 'INFO')}},
}
