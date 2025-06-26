import environ
import os

from pathlib import Path

from .env import env

BASE_DIR = Path(__file__).resolve().parent.parent
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

SECRET_KEY = env('SECRET_KEY')

DEBUG = True

ALLOWED_HOSTS = ['*']


INSTALLED_APPS = [
    'rest_framework',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
]

INSTALLED_EXTENSION = [
    'api_accounts',
    'api_medical_records',
    'api_token_jwt',
    'api_visits',
    'api_statistic',
]

INSTALLED_APPS += INSTALLED_EXTENSION

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
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

WSGI_APPLICATION = 'core.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH0_DOMAIN = env.str('AUTH0_DOMAIN')
AUTH0_CLIENT_ID = env.str('AUTH0_CLIENT_ID')
AUTH0_CLIENT_SECRET = env.str('AUTH0_CLIENT_SECRET')
AUTH0_CALLBACK_URL = env.str('AUTH0_CALLBACK_URL')
AUTH0_AUDIENCE = env.str('AUTH0_AUDIENCE')
LOGOUT_REDIRECT_URL = env.str('LOGOUT_REDIRECT_URL')

ACCOUNTS_SERVICE_URL = "http://web-accounts:8100"
VISITS_SERVICE_URL = "http://web-visits:8600"
MEDICAL_RECORDS_SERVICE_URL = "http://web-medical-records:8300"
PAYMENTS_SERVICE_URL = "http://web-payments:8500"
TOKEN_URL = env.str('TOKEN_URL')
