from django.conf import settings
from django.core.files.base import ContentFile
from io import BytesIO
from PIL import Image

from apps.api.models import Sessions, Review

import random
import string

def authenticate(token):
    ses_check = Sessions.objects.filter(token = token, on_session = True)
    if ses_check.exists():
        return ses_check.first()
    return None

def user_rating(account):
    rating = 0
    reviews = Review.objects.filter(reviewee = account)

    for review in reviews:
        rating += review.rating
    
    if rating != 0:
        return "%.1f" % (rating/len(reviews))
    else:
        return rating

def random_token():
    key = ""
    for x in range(0, 50):
      num = random.randrange(0, 26)
      if num > len(string.digits)-1:
      	key += string.ascii_lowercase[num]
      else:
      	key += string.digits[num]
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
