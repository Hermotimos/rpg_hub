"""GoogleCloudStorage extension classes for MEDIA and STATIC uploads """

from django.conf import settings
from storages.backends.gcloud import GoogleCloudStorage
from storages.utils import setting
from urllib.parse import urljoin


class GoogleCloudStaticFileStorage(GoogleCloudStorage):
    """Google file storage class which gives a static file path from STATIC_URL not google generated one."""
    bucket_name = setting('GS_BUCKET_NAME')
    location = 'static'

    def url(self, name):
        """Gives correct STATIC_URL and not google generated url."""
        print('STATIC',  settings.STATIC_URL, name, '//', urljoin(settings.STATIC_URL, name))
        return urljoin(settings.STATIC_URL, name)


class GoogleCloudMediaFileStorage(GoogleCloudStorage):
    """Google file storage class which gives a media file path from MEDIA_URL not google generated one."""
    bucket_name = setting('GS_BUCKET_NAME')
    location = 'media'

    def url(self, name):
        """Gives correct MEDIA_URL and not google generated url."""
        print('MEDIA', settings.MEDIA_URL, name, '//', urljoin(settings.MEDIA_URL, name))
        return urljoin(settings.MEDIA_URL, name)

