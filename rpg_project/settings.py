import json
import os

from django.core.exceptions import ImproperlyConfigured
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_secret(setting):
    """Get secret setting or fail with ImproperlyConfigured"""
    with open(os.path.join(f'{BASE_DIR}/rpg_project/', 'secret.json')) as f:
        secrets = json.load(f)
    try:
        return secrets[setting]
    except KeyError:
        raise ImproperlyConfigured(f"Set the {setting} setting")


SECRET_KEY = get_secret('SECRET_KEY')
DEBUG = True
ALLOWED_HOSTS = [
    '127.0.0.1',
    'hyllemath.pythonanywhere.com',
    'burkelt.pythonanywhere.com',
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # imported
    'crispy_forms',
    'debug_toolbar',
    'django_filters',
    'ckeditor',

    # own
    'chronicles',
    'communications',
    'contact',
    'imaginarion',
    'knowledge',
    'rules',
    'prosoponomikon',
    'technicalities',
    'toponomikon',
    'users.apps.UsersConfig',  # just another way of doing this
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

    
ROOT_URLCONF = 'rpg_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'libraries': {
                'custom_filters': 'templatetags.custom_filters',
            },
            # 'loaders': [
            #      'django.template.loaders.filesystem.Loader',
            #      'django.template.loaders.app_directories.Loader',
            #   ],
        },
    },
]

WSGI_APPLICATION = 'rpg_project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
    # 'default': {
    #     'ENGINE': 'django.db.backends.postgresql_psycopg2',
    #     'NAME': get_secret('POSTGRES_DBNAME'),
    #     'USER': get_secret('POSTGRES_USER'),
    #     'PASSWORD': get_secret('POSTGRES_PASSWORD'),
    #     'HOST': get_secret('POSTGRES_HOST'),
    #     'PORT': get_secret('POSTGRES_PORT'),
    #
    # }
}

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators
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
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'pl'

TIME_ZONE = 'Europe/Warsaw'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

# [custom] Following configuration is suitable for development:
STATIC_ROOT = 'rpg_project/static'
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]


MEDIA_ROOT = os.path.join(BASE_DIR, 'media')        # path to uploaded pics
MEDIA_URL = '/media/'                               # url to media

CRISPY_TEMPLATE_PACK = 'bootstrap4'

LOGIN_REDIRECT_URL = 'users:home'
LOGIN_URL = 'users:login'
LOGOUT_REDIRECT_URL = 'users:login'

# With 2-step verification turn off:
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_USE_TLS = True
# EMAIL_PORT = 587
# EMAIL_HOST_USER = get_secret('EMAIL_HOST_USER')
# EMAIL_HOST_PASSWORD = get_secret('EMAIL_HOST_PASSWORD')


# With 2-step verification turn on:
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = get_secret('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = get_secret('EMAIL_HOST_PASSWORD_TWO_STEP')


# -----------------------------------------------------------------------------

# debug-toolbar
INTERNAL_IPS = ['127.0.0.1', ]
# debug-toolbar not rendering problem:
# https://www.taricorp.net/2020/windows-mime-pitfalls/
# https://stackoverflow.com/questions/16303098/django-development-server-and-mime-types/64055514#64055514
# After editing registry - restart local server for changes to take effect


# -----------------------------------------------------------------------------

# django-ckeditor
# Online tool for CDEditor Toolbar customizations, but it produces JS:
# https://ckeditor.com/latest/samples/toolbarconfigurator/index.html#basic
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',
    },
}

