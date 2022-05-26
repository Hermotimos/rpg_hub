import os
from urllib.parse import urljoin

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from google.cloud import storage
from storages.backends.gcloud import GoogleCloudStorage
from storages.utils import setting


# ----------------------------------------------------------------------------

#
# class ReplaceFileStorage(FileSystemStorage):
#
#     def get_available_name(self, name, max_length=None):
#         """
#         Returns a filename that's free on the target storage system, and
#         available for new content to be written to.
#         Found at http://djangosnippets.org/snippets/976/
#         This file storage solves overwrite on upload problem.
#         """
#         # If the filename already exists, remove it
#         if self.exists(name):
#             os.remove(os.path.join(settings.MEDIA_ROOT, name))
#         return name
    
    # Commented out: the reason for replacing whitespaces with underscores is
    # that a valid url cannot be formed with whitespaces
    # def get_valid_name(self, name):
    #     """Overrides method which would normally replace whitespaces with
    #     underscores and remove special characters.
    #         s = str(s).strip().replace(' ', '_')
    #         return re.sub(r'(?u)[^-\w.]', '', s)
    #     Modified to leave whitespace and to accept it in regular expressions.
    #     """
    #     name = str(name).strip()
    #     return re.sub(r'(?u)[^-\w.\s]', '', name)


# ----------------------------------------------------------------------------


class GoogleCloudStaticFileStorage(GoogleCloudStorage):
    """Google file storage class which gives a static file path from STATIC_URL
     not google generated one.
     """
    bucket_name = setting('GS_BUCKET_NAME')
    location = 'static'

    def url(self, name):
        """Gives correct STATIC_URL and not google generated url."""
        print('STATIC',  settings.STATIC_URL, name, '//', urljoin(settings.STATIC_URL, name))
        return urljoin(settings.STATIC_URL, name)


class GoogleCloudMediaFileStorage(GoogleCloudStorage):
    """Google file storage class which gives a media file path from MEDIA_URL
    not google generated one.
    """
    bucket_name = setting('GS_BUCKET_NAME')
    location = 'media'

    def url(self, name):
        """Gives correct MEDIA_URL and not google generated url."""
        print('MEDIA', settings.MEDIA_URL, name, '//', urljoin(settings.MEDIA_URL, name))
        return urljoin(settings.MEDIA_URL, name)


def upload_to_bucket(destination_path, source_path, bucket_name):
    # This isn't used at the time, but might be useful as a template
    storage_client = storage.Client.from_service_account_json(
        settings.GOOGLE_APPLICATION_CREDENTIALS)
    bucket = storage_client.get_bucket(bucket_name)
    
    blob = bucket.blob(destination_path)
    blob.upload_from_filename(source_path)
    
    return blob.public_url


# ----------------------------------------------------------------------------
