"""
Django settings for FreeItLessons project.

Every deployment specific value can be overridden with an environment
variable (see README.md, section "Configuration").

https://docs.djangoproject.com/en/stable/topics/settings/
https://docs.djangoproject.com/en/stable/ref/settings/
"""
import os
import sys
from datetime import timedelta
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from django.core.management.utils import get_random_secret_key
from django.utils.csp import CSP


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


def _local_development_secret_key():
    """Random key for DJANGO_DEBUG=1 without DJANGO_SECRET_KEY: generated once and
    kept in .django-dev-secret-key (git ignored), so sessions survive restarts and
    all processes agree; in memory only when the project folder is read-only."""
    path = BASE_DIR / '.django-dev-secret-key'
    try:
        return path.read_text().strip()
    except FileNotFoundError:
        key = get_random_secret_key()
        try:
            path.write_text(key)
            path.chmod(0o600)
        except OSError:
            pass
        return key


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env_bool('DJANGO_DEBUG', False)

# SECURITY WARNING: keep the secret key used in production secret!
# (the key formerly committed to this repository is public - never reuse it)
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', '')
if not SECRET_KEY:
    if not DEBUG:
        raise ImproperlyConfigured('Set the DJANGO_SECRET_KEY environment variable '
                                   '(or DJANGO_DEBUG=1 for local development).')
    SECRET_KEY = _local_development_secret_key()

ALLOWED_HOSTS = env_list('DJANGO_ALLOWED_HOSTS', ['127.0.0.1', 'localhost'])
CSRF_TRUSTED_ORIGINS = env_list('DJANGO_CSRF_TRUSTED_ORIGINS', [])

# HTTPS hardening - enable when served over TLS (see README "Configuration")
SECURE_SSL_REDIRECT = env_bool('DJANGO_SECURE_SSL_REDIRECT', False)
SESSION_COOKIE_SECURE = env_bool('DJANGO_SECURE_COOKIES', False)
CSRF_COOKIE_SECURE = SESSION_COOKIE_SECURE
SECURE_HSTS_SECONDS = int(os.environ.get('DJANGO_SECURE_HSTS_SECONDS', '0'))
SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool('DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS', False)
BEHIND_TLS_PROXY = env_bool('DJANGO_BEHIND_TLS_PROXY', False)
if BEHIND_TLS_PROXY:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_HTTPONLY = True
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = 'same-origin'

# Content Security Policy: scripts only from this site (the React bundle, the
# admin), no inline scripts, plugins or framing. Styles may be inline (style
# attributes of the course contents, CodeMirror) and come from the two CDNs the
# pages use; images may come from any web address (course material).
BOOTSTRAP_CDN = 'https://stackpath.bootstrapcdn.com'
SECURE_CSP = {
    'default-src': [CSP.SELF],
    'script-src': [CSP.SELF],
    'style-src': [CSP.SELF, CSP.UNSAFE_INLINE, BOOTSTRAP_CDN, 'https://cdnjs.cloudflare.com'],
    'font-src': [CSP.SELF, BOOTSTRAP_CDN],
    'img-src': [CSP.SELF, 'data:', 'https:', 'http:'],
    'connect-src': [CSP.SELF],
    'object-src': [CSP.NONE],
    'base-uri': [CSP.SELF],
    'form-action': [CSP.SELF],
    'frame-ancestors': [CSP.NONE],
}

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
    'axes',
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
    'django.middleware.csp.ContentSecurityPolicyMiddleware',
    # login throttling - keep it last (django-axes)
    'axes.middleware.AxesMiddleware',
]

AUTHENTICATION_BACKENDS = [
    # django-axes first: refuses the login while the (username, IP) pair is locked out
    'axes.backends.AxesStandaloneBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# Login throttling (mainapp/login_throttling.py): after AXES_FAILURE_LIMIT wrong
# passwords for one username from one IP address that pair is locked out for
# AXES_COOLOFF_TIME; a correct login resets the counter.
AXES_FAILURE_LIMIT = int(os.environ.get('DJANGO_LOGIN_FAILURE_LIMIT', '5'))
AXES_COOLOFF_TIME = timedelta(minutes=int(os.environ.get('DJANGO_LOGIN_COOLOFF_MINUTES', '15')))
AXES_LOCKOUT_PARAMETERS = [['username', 'ip_address']]
AXES_RESET_ON_SUCCESS = True
AXES_CLIENT_IP_CALLABLE = 'mainapp.login_throttling.client_ip'
AXES_LOCKOUT_CALLABLE = 'mainapp.login_throttling.lockout_response'
# no log of successful logins (IP address + browser of every student)
AXES_DISABLE_ACCESS_LOG = True

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
                'mainapp.context_processors.frontend',
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

CONTACT_FORM_SUBJECT_TEMPLATE_NAME = 'email_subject.txt'
CONTACT_FORM_MESSAGE_TEMPLATE_NAME = 'email_message.txt'


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

# Parent directory of the private per-run directories (None = the system default).
TEMP_SOLUTION_CODE_BLOCK = os.environ.get('TEMP_SOLUTION_CODE_BLOCK') or None

# Limits of a single run of a student's program (mainapp/sandbox.py)
CODE_RUN_TIMEOUT_SECONDS = int(os.environ.get('CODE_RUN_TIMEOUT_SECONDS', '5'))
CODE_RUN_MEMORY_MB = int(os.environ.get('CODE_RUN_MEMORY_MB', '256'))
CODE_RUN_OUTPUT_KB = int(os.environ.get('CODE_RUN_OUTPUT_KB', '256'))
CODE_RUN_MAX_CODE_KB = int(os.environ.get('CODE_RUN_MAX_CODE_KB', '64'))

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {'console': {'class': 'logging.StreamHandler'}},
    'loggers': {'mainapp': {'handlers': ['console'], 'level': os.environ.get('DJANGO_LOG_LEVEL', 'INFO')}},
}
