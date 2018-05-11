from distutils.version import StrictVersion
from os import path

import django

DJANGO_VERSION = StrictVersion(django.get_version())

# set the django DEBUG option
DEBUG = True

PERIMETER_ENABLED = True

ROOT_URLCONF = 'test_app.urls'

# this isn't used, but Django likes having something here for running the tests
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'delme'
    }
}

# NB - this is good for local testing only
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
STATIC_URL = '/static/'
STATIC_ROOT = path.abspath(path.join(path.dirname(__file__), '..', 'static'))

INSTALLED_APPS = (
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'perimeter',
    'test_app',
)

ACTUAL_MIDDLEWARE_CLASSES = [
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'perimeter.middleware.PerimeterAccessMiddleware',
]

if DJANGO_VERSION < StrictVersion('1.10.0'):
    MIDDLEWARE_CLASSES = ACTUAL_MIDDLEWARE_CLASSES
else:
    MIDDLEWARE = ACTUAL_MIDDLEWARE_CLASSES

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
            'level': 'INFO',
        },
    }
}

PROJECT_DIR = path.abspath(path.join(path.dirname(__file__)))

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            path.join(PROJECT_DIR, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    }
]
