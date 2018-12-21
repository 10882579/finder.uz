from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings

class MediaStorage(S3Boto3Storage):
    location = 'account-photos'
    file_overwrite = False

class PostPhotosStorage(S3Boto3Storage):
    location = 'post-photos'
    file_overwrite = False
