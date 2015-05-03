"""Test app settings."""
from os import environ

# set the django DEBUG option
DEBUG = environ.get('DJANGO_DEBUG', 'true').lower() == 'true'

ROOT_URLCONF = 'test_app.urls'

# this isn't used, but Django likes having something here for running the tests
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'delme'
    }
}

# ================= APP SETTINGS =================
PERIMETER_ENABLED = True
# ================= / APP SETTINGS ===============

INSTALLED_APPS = (
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.sessions',
    'perimeter',
    'test_app',
    # uncomment to enable the coverage tests to run
    # 'django_coverage',
)

# none required, but need to explicitly state this for Django 1.7
MIDDLEWARE_CLASSES = [
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'perimeter.middleware.PerimeterAccessMiddleware',
]

SECRET_KEY = "something really, really hard to guess goes here."

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'DEBUG',
        },
    }
}

# COVERAGE_REPORT_HTML_OUTPUT_DIR = 'coverage_reports'
# COVERAGE_CUSTOM_REPORTS = False