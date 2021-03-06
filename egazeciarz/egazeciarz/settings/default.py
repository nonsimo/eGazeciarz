"""
Django settings for egazeciarz project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


ADMINS = (
    ('Patryk Perduta', 'pperduta@spistresci.pl'),
    ('Krzysztof Szumny', 'kszumny@spistresci.pl'),
    ('Artur Stachecki', 'arturstachecki@gmail.com'),
    ('Mateusz Smolik', 'dyzajash@gmail.com'),
)

USER = ''
PASSWORD = ''

settings_module = os.environ.get("DJANGO_SETTINGS_MODULE")


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

TEMPLATE_DEBUG = False

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = (
    # django staff
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    # our apps
    'egazeciarz',
    'services',
    # else
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.facebook',
    'django_nose',
    'south',
    'widget_tweaks',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'egazeciarz.urls'

WSGI_APPLICATION = 'egazeciarz.wsgi.application'

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'pl'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

# Django allauth section

SITE_ID = 1  # IMPORTANT! After installation change example.com in /admin panel

ACCOUNT_AUTHENTICATION_METHOD = "email"  # login only via email
ACCOUNT_EMAIL_REQUIRED = True

AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of `allauth`
    "django.contrib.auth.backends.ModelBackend",
    # `allauth` specific authentication methods, such as login by e-mail
    "allauth.account.auth_backends.AuthenticationBackend",
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.request",
    "django.contrib.auth.context_processors.auth",
    "egazeciarz.settings.context_processors.context_processor",
    "allauth.account.context_processors.account",
    "allauth.socialaccount.context_processors.socialaccount",
)

# auth and allauth settings
LOGIN_REDIRECT_URL = '/'  # success redirect
SOCIALACCOUNT_QUERY_EMAIL = True
SOCIALACCOUNT_PROVIDERS = {
    'facebook': {
        'SCOPE': ['email', 'publish_stream'],
        'METHOD': 'js_sdk'
    }
}

# Template files
TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(BASE_DIR), "static", "templates")
)

STATIC_ROOT = os.path.join(
    os.path.dirname(BASE_DIR),
    "egazeciarz",
    "collected_statics",
)

IS_DEV = 'egazeciarz.settings.development' == settings_module
IS_TEST = 'egazeciarz.settings.test' == settings_module
IS_STAGING = 'egazeciarz.settings.staging' == settings_module
IS_PROD = 'egazeciarz.settings.production' == settings_module

ENV = settings_module.split('.')[-1]


if IS_STAGING or IS_PROD:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


try:
    from local_settings import *
except ImportError:
    print 'Error: cannot import local_settings'
    exit()
