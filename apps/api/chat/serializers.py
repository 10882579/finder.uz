from django.conf import settings
from django.db.models import Q
from rest_framework.serializers import ModelSerializer
from apps.api.models import ChatRoom, Message

from apps.api.functions import user_rating

class ConversationSerializer(ModelSerializer):
    class Meta:
        model = ChatRoom
        fields = [
            'id'
        ]

    def get_user_image(self, account):
        if account.image:
            return account.image.url
        return settings.DEFAULT_MALE_IMG

    def to_representation(self, instance):
        ret = super().to_representation(instance)

        if instance.first == self.context['account']:
            ret['account_id']   = instance.second.id
            ret['first_name']   = instance.second.user.first_name
            ret['last_name']    = instance.second.user.last_name
            ret['image']        = self.get_user_image(instance.second)
            ret['rating']       = user_rating(instance.second)

        elif instance.second == self.context['account']:
            ret['account_id']   = instance.first.id
            ret['first_name']   = instance.first.user.first_name
            ret['last_name']    = instance.first.user.last_name
            ret['image']        = self.get_user_image(instance.first)
            ret['rating']       = user_rating(instance.first)

        ret['room'] = instance.room

        return ret

class MessageSerializer(ModelSerializer):
    class Meta:
        model = Message
        fields = [
            'message',
        ]

    def to_representation(self, instance):
        ret = super().to_representation(instance)

        ret['from']         = instance.sender.id
        ret['created_at']   = instance.created_at.timestamp() * 1000

        return ret