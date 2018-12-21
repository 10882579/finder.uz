from django.conf import settings
from django.core.files.base import ContentFile
from io import BytesIO
from PIL import Image

from apps.api.models import Sessions

import random

letters = ('a', 'b', 'c', 'd','e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z')
numbers = ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9')


def authenticate(token):
    ses_check = Sessions.objects.filter(token = token, on_session = True)
    if ses_check.exists():
        return ses_check.first()
    return None


def random_token():
    key = ""
    for x in range(0, 50):
      num = random.randrange(0, 26)
      if num > len(numbers)-1:
      	key += letters[num]
      else:
      	key += numbers[num]
    return key.lower()

def thumbnail(**kwargs):
    image   = kwargs.get('image')
    folder  = kwargs.get('folder')
    size    = kwargs.get('size')
    if image is not None:

        if settings.DEBUG:
            folder = 'TEST'

        img_io = BytesIO()
        img = Image.open(image)
        img.thumbnail(size)
        img.save(img_io, format=img.format.lower(), quality=100)

        return ContentFile(img_io.getvalue(), '%s/%s.%s' % (folder, random_token(), img.format.lower()))

    return image
