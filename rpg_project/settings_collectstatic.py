
from rpg_project.settings import *

"""
This file is for "collecting" static files from the local machine to Storage bucket

    1)
    In manage.py temporarily replace:

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rpg_project.settings')
    with
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rpg_project.settings_collectstatic')

    2) python manage.py collectstatic

    3) Revert changes in manage.py and settings.py

"""

GS_BUCKET_NAME = env("GS_BUCKET_NAME")
STATIC_URL = f"https://storage.googleapis.com/{GS_BUCKET_NAME}/"
GS_LOCATION = "static"
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
DEFAULT_FILE_STORAGE = 'rpg_project.storages.GoogleCloudMediaFileStorage'
STATICFILES_STORAGE = 'rpg_project.storages.GoogleCloudStaticFileStorage'


GOOGLE_APPLICATION_CREDENTIALS = env("GOOGLE_APPLICATION_CREDENTIALS")
GS_CREDENTIALS = service_account.Credentials.from_service_account_file(
    GOOGLE_APPLICATION_CREDENTIALS)


# MEDIA_ROOT = os.path.join(BASE_DIR, 'media')        # path to uploaded pics
# MEDIA_URL = '/media/'                               # url to media


