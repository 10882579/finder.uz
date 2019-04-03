from django.conf import settings
from django.db.models import Q

from rest_framework.serializers import (
    ModelSerializer,
    Serializer,
    CharField,
    FileField
)

from apps.api.models import UserAccount, User, UserAccountFollowers, Posts, PostPhotos, UserSavedPosts
from apps.api.functions import thumbnail

import bcrypt
import re

re_email            = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
re_numeric          = re.compile(r'[0-9]+$')
re_alphanumeric     = re.compile(r'[a-z0-9]+$')
re_alphabetic       = re.compile(r'[a-zA-Z]+$')

class UserAccountSerializer(ModelSerializer):
    class Meta:
        model = UserAccount
        fields = ['email']

    def to_representation(self, instance):
        ret = super().to_representation(instance)

        image = ''
        if instance.image:
            image = instance.image.url
        else:
            image = settings.DEFAULT_MALE_IMG

        ret['account_id']       = instance.id
        ret['first_name']       = instance.user.first_name
        ret['last_name']        = instance.user.last_name
        ret['image']            = image
        return ret

class UserLoginSerializer(Serializer):
    entry       = CharField(required = True)
    password    = CharField(required = True)
    class Meta:
        model = UserAccount
        fields = (
            'entry',
            'password'
        )

    def validate(self, data):

        entry       = data.get('entry')
        password    = data.get('password')

        errors = []

        account = UserAccount.objects.filter(
            Q(email = entry) |
            Q(phone_number = entry)
        )
        if not account.exists():
            errors.append("Email/Telefon raqam yoki parolingiz noto'g'ri. Iltimos qayta kiriting!")

        elif account.exists():
            if not account.first().check_password(password):
                errors.append("Email/Telefon raqam yoki parolingiz noto'g'ri. Iltimos qayta kiriting!")
            elif account.first().check_password(password):
                data['account'] = account.first()

        if len(errors) > 0:
            data['errors'] = errors

        return data

class UserRegistrationSerializer(Serializer):
    first_name      = CharField(required = True)
    last_name       = CharField(required = True)
    email           = CharField(required = True)
    phone_number    = CharField(required = True)
    password        = CharField(required = True)
    class Meta:
        model = UserAccount
        fields = [
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'password'
        ]

    def check_email_if_exists(self, email):
        email = UserAccount.objects.filter(email = email)
        if email.exists():
            return False
        return True

    def check_phone_if_exists(self, phone_number):
        phone = UserAccount.objects.filter(phone_number = phone_number)
        if phone.exists():
            return False
        return True

    def validate(self, data):
        first_name          = data.get('first_name')
        last_name           = data.get('last_name')
        email               = data.get('email')
        phone_number        = data.get('phone_number')
        password            = data.get('password')

        errors = []

        if len(first_name) < 2 or not re_alphabetic.match(first_name):
            errors.append("Ism ikki yoki undan ortiq va faqat harflardan iborat bo'lishi kerak!")

        if len(last_name) < 2 or not re_alphabetic.match(last_name):
            errors.append("Familiya ikki yoki undan ortiq va faqat harflardan iborat bo'lishi kerak!")

        if not self.check_email_if_exists(email):
            errors.append('Kiritilgan email band!')

        if not re_email.match(email):
            errors.append("Kiritilgan email noto'gri kiritilgan!")

        if not self.check_phone_if_exists(phone_number):
            errors.append('Kiritilgan telefon raqam band!')

        if not re_numeric.match(phone_number):
            errors.append('Kiritilgan telefon raqam noto\'g\'ri!')

        if len(password) < 7 or not re_alphanumeric.match(password):
            errors.append('Kiritilgan yashirin kod 7 yoki undan ortiq raqam yoki harflardan iborat bo\'lishi kerak!')

        if len(errors) > 0:
            data['errors'] = errors

        return data

    def create(self):
        password        = self.validated_data.get('password')
        first_name      = self.validated_data.get('first_name')
        last_name       = self.validated_data.get('last_name')
        email           = self.validated_data.get('email')
        phone_number    = self.validated_data.get('phone_number')
        if password and first_name and last_name and email and phone_number:

            user = User.objects.create(
                first_name  = first_name.capitalize(),
                last_name   = last_name.capitalize()
            )

            return UserAccount.objects.create(
                user            = user,
                email           = email,
                phone_number    = phone_number,
                password        = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
            )

        return None

class UserAccountUpdateSerializer(Serializer):
    first_name      = CharField(required = False)
    last_name       = CharField(required = False)
    phone_number    = CharField(required = False)
    email           = CharField(required = False)
    username        = CharField(required = False)
    password        = CharField(required = False)
    image           = FileField(required = False)
    class Meta:
        model = UserAccount
        fields = [
            'first_name',
            'last_name',
            'phone_number',
            'email',
            'username',
            'password',
            'image'
        ]

    def check(self, entry):
        account = UserAccount.objects.filter(
            Q(email = entry) |
            Q(phone_number = entry)
        )
        if account.exists():
            return True
        return None

    def validate(self, data):
        first_name      = data.get('first_name')
        last_name       = data.get('last_name')
        phone_number    = data.get('phone_number')
        email           = data.get('email')
        password        = data.get('password')
        image           = data.get('image')

        errors = []

        if image is None:
            if first_name:
                if len(first_name) < 2 or not re_alphabetic.match(first_name):
                    errors.append("Ism ikki yoki undan ortiq va faqat harflardan iborat bo'lishi kerak!")
            if last_name:
                if len(last_name) < 2 or not re_alphabetic.match(last_name):
                    errors.append("Familiya ikki yoki undan ortiq va faqat harflardan iborat bo'lishi kerak!")
            if phone_number:
                if not re_numeric.match(phone_number) or len(phone_number) < 12:
                    errors.append('Kiritilgan telefon raqam noto\'g\'ri!')
                elif self.check(phone_number) is not None:
                    errors.append('Kiritilgan telefon raqam band!')
            if email:
                if not re_email.match(email):
                    errors.append('Kiritilgan email noto\'g\'ri!')
                elif self.check(email) is not None:
                    errors.append('Kiritilgan email band!')

            if not password:
                errors.append('Kiritilgan yashirin kod noto\'g\'ri!')
            elif self.context.get('account').check_password(password) is not True:
                errors.append('Kiritilgan yashirin kod noto\'g\'ri!')

        if len(errors) > 0:
            data['errors'] = errors

        return data

    def save(self):
        account    = self.context.get('account')
        image      = self.validated_data.get('image')
        if image:
            self.validated_data['image'] = thumbnail(folder = account.id, image = image, size = (350,350))
        account.user.update(**self.validated_data)
        account.update(**self.validated_data)

class UserAccountByIdSerializer(Serializer):
    class Meta:
        model = UserAccount
        fields = ['id']

    def to_representation(self, instance):
        ret = super().to_representation(instance)

        image = ''
        if instance.image:
            image = instance.image.url
        else:
            image = settings.DEFAULT_MALE_IMG
            
        ret['account_id']   = instance.id
        ret['first_name']   = instance.user.first_name
        ret['last_name']    = instance.user.last_name
        ret['image']        = image
        return ret

class UserAccountFollowingsSerializer(Serializer):
    class Meta:
        model = UserAccountFollowers
        fields = ['id']

    def to_representation(self, instance):
        ret = super().to_representation(instance)

        image = ''
        if instance.following.image:
            image = instance.following.image.url
        else:
            image = settings.DEFAULT_MALE_IMG

        ret['id']           = instance.following.id
        ret['first_name']   = instance.following.user.first_name
        ret['last_name']    = instance.following.user.last_name
        ret['image']        = image
        ret['following']    = True
        return ret

class UserPostListSerializer(ModelSerializer):
    class Meta:
        model = Posts
        fields = [
            'id',
            'title',
            'price',
            'sold',
            'premium',
            'posted'
        ]

    def get_post_photos(self, post):
        return [{ 'id': photo.id, 'uri': photo.image.url } for photo in PostPhotos.objects.filter(post = post)]

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['photos'] = self.get_post_photos(instance.id)
        ret['created_at'] = instance.created_at.timestamp() * 1000
        return ret

class UserSavedPostListSerializer(ModelSerializer):
    class Meta:
        model = UserSavedPosts
        fields = []

    def get_post_photos(self, post):
        return [{ 'id': photo.id, 'uri': photo.image.url } for photo in PostPhotos.objects.filter(post = post)]

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['id']       = instance.post.id
        ret['title']    = instance.post.title
        ret['price']    = instance.post.price
        ret['sold']     = instance.post.sold
        ret['photos']   = self.get_post_photos(instance.post)
        ret['created_at'] = instance.created_at.timestamp() * 1000
        return ret
