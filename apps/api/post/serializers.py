from django.conf import settings
from django.db.models import Q

from rest_framework.serializers import (
    ModelSerializer,
    Serializer,
    CharField,
    ListField, FileField
)

from apps.api.models import Posts, PostPhotos, Review
from apps.api.functions import thumbnail, user_rating

class CreatePostSerializer(ModelSerializer):
    image           = ListField(child = FileField(max_length=100000, allow_empty_file=True))
    class Meta:
        model = Posts
        fields = [
            'title',
            'category',
            'condition',
            'description',
            'price',
            'negotiable',
            'city_town',
            'state',
            'image',
        ]


    def validate(self, data):
        title           = data.get('title')
        category        = data.get('category')
        condition       = data.get('condition')
        description     = data.get('description')
        price           = data.get('price')
        negotiable      = data.get('negotiable')
        city_town       = data.get('city_town')
        state           = data.get('state')
        image           = data.get('image')

        errors = []

        if not title or not category or not condition or not price or not city_town or not state or len(image) == 0 or not description:
            errors.append('Barcha ma\'lumotlarni kiriting!')

        if len(errors) > 0:
            data['errors'] = errors
        return data

    def save(self):
        image       = self.validated_data.get('image')
        account     = self.context.get('account')
        self.validated_data.pop('image')

        self.validated_data['account'] = account
        id = Posts.objects.create(**self.validated_data)

        for file in image:
            img = thumbnail(account = account, image = file, size = (350, 350))
            PostPhotos.objects.create(post = id, image = img)

    def update(self):
        post        = self.context.get('post')
        image       = self.validated_data.get('image')

        post_photos = PostPhotos.objects.filter(post=post)

        for photo in post_photos:
            photo.image.delete()
            photo.delete()
        for file in image:
            img = thumbnail(account = post.account, image = file, size = (350, 350))
            PostPhotos.objects.create(post = post, image = img)


class PostListSerializer(ModelSerializer):
    class Meta:
        model = Posts
        fields = [
            'id',
            'price'
        ]

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['photos'] = { 'uri': PostPhotos.objects.filter(post = instance.id)[0].image.url }
        return ret

class PostByIdSerializer(ModelSerializer):
    class Meta:
        model = Posts
        fields = [
            'id',
            'title',
            'category',
            'condition',
            'description',
            'price',
            'negotiable',
            'city_town',
            'state',
            'sold',
            'premium'
        ]

    def get_user_image(self, account):
        if account.image:
            return account.image.url
        return settings.DEFAULT_MALE_IMG

    def get_post_account(self, account):

        return {
            'account_id':   account.id,
            'first_name':   account.user.first_name,
            'last_name':    account.user.last_name,
            'image':        self.get_user_image(account),
            'rating':       user_rating(account)
        }

    def get_post_photos(self, post):
        return [{'uri': photo.image.url } for photo in PostPhotos.objects.filter(post = post)]

    def to_representation(self, instance):
        ret                 = super().to_representation(instance)
        ret['account']      = self.get_post_account(instance.account)
        ret['photos']       = self.get_post_photos(instance.id)
        ret['created_at']   = instance.created_at.timestamp() * 1000
        return ret
