import io
import os
from urllib.parse import urlparse

import environ
from google.cloud import secretmanager
from google.oauth2 import service_account


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# -----------------------------------------------------------------------------


# [START gaestd_py_django_secret_config]

env = environ.Env(DEBUG=(bool, False))
env_file = os.path.join(BASE_DIR, ".env")

# Use a local secret file, if provided
if os.path.isfile(env_file):
    env.read_env(env_file)
    
# [START_EXCLUDE]
# Create local settings if running with CI, for unit testing
elif os.getenv("TRAMPOLINE_CI", None):
    placeholder = (
        f"SECRET_KEY=a\n"
        f"DATABASE_URL=sqlite://{os.path.join(BASE_DIR, 'db.sqlite3')}"
    )
    env.read_env(io.StringIO(placeholder))
# [END_EXCLUDE]

# Pull secrets from Secret Manager
elif os.environ.get("GOOGLE_CLOUD_PROJECT", None):
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    client = secretmanager.SecretManagerServiceClient()
    settings_name = os.environ.get("SETTINGS_NAME", "django_settings")
    name = f"projects/{project_id}/secrets/{settings_name}/versions/latest"
    payload = client.access_secret_version(name=name).payload.data.decode("UTF-8")
    
    env.read_env(io.StringIO(payload))
else:
    raise Exception("No local .env or GOOGLE_CLOUD_PROJECT detected. No secrets found.")

# [END gaestd_py_django_secret_config]


# -----------------------------------------------------------------------------


SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG")


# -----------------------------------------------------------------------------


# [START gaestd_py_django_csrf]

# SECURITY WARNING: It's recommended that you use this when running in production.
# The URL will be known once you first deploy to App Engine.
# This code takes the URL and converts it to both these settings formats.

APPENGINE_URL = env("APPENGINE_URL", default=None)
if APPENGINE_URL:
    # Ensure a scheme is present in the URL before it's processed.
    if not urlparse(APPENGINE_URL).scheme:
        APPENGINE_URL = f"https://{APPENGINE_URL}"

    # ALLOWED_HOSTS = [urlparse(APPENGINE_URL).netloc]
    # For enabling older app versions to host site
    ALLOWED_HOSTS = ['*']
    
    CSRF_TRUSTED_ORIGINS = [APPENGINE_URL]
    SECURE_SSL_REDIRECT = True
else:
    CSRF_TRUSTED_ORIGINS = [
        'https://8000-cs-570532252862-default.cs-europe-west4-fycr.cloudshell.dev'
    ]
    ALLOWED_HOSTS = [
        '127.0.0.1',
        'hyllemath.pythonanywhere.com',
        'burkelt.pythonanywhere.com',
        'hyllemath.lm.r.appspot.com',
    ]
    
# [END gaestd_py_django_csrf]


# -----------------------------------------------------------------------------


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


# -----------------------------------------------------------------------------
# Database

if os.getenv('GAE_ENV', '').startswith('standard'):
    # Requires DATABASE_URL environmental variable to be set
    DATABASES = {"default": env.db()}
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }
    
# Use a in-memory sqlite3 database when testing in CI systems
if os.getenv("TRAMPOLINE_CI", None):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
        }
    }
    
    
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'


# -----------------------------------------------------------------------------
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

# -----------------------------------------------------------------------------
# Internationalization

# https://docs.djangoproject.com/en/2.2/topics/i18n/
LANGUAGE_CODE = 'pl'
TIME_ZONE = 'Europe/Warsaw'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# -----------------------------------------------------------------------------
# Static files (CSS, JavaScript, Images)

# https://docs.djangoproject.com/en/2.2/howto/static-files/

if os.getenv('GAE_ENV', '').startswith('standard'):
    GS_BUCKET_NAME = env("GS_BUCKET_NAME")
    STATIC_URL = f"https://storage.googleapis.com/{GS_BUCKET_NAME}/static/"
    STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
    DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
    STATICFILES_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
    # from django.core.files.storage import default_storage
    # print(default_storage.__class__)

    GOOGLE_APPLICATION_CREDENTIALS = env("GOOGLE_APPLICATION_CREDENTIALS")
    print(os.getcwd())
    GS_CREDENTIALS = service_account.Credentials.from_service_account_file(
        GOOGLE_APPLICATION_CREDENTIALS)

else:
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
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD_TWO_STEP')


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
