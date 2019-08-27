from django.conf import settings
from rest_framework.serializers import ModelSerializer
from apps.api.models import Notification

class NotificationListSerializer(ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            'id',
            'read',
            'title',
            'message',
        ]

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['created_at']   = instance.created_at.timestamp() * 1000
        return ret