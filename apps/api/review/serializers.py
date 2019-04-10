from django.conf import settings
from rest_framework.serializers import ModelSerializer

from apps.api.models import Review

class AccountReviewsSerializer(ModelSerializer):

    class Meta:
        model = Review
        fields = [
            'id',
            'rating',
            'review',
        ]

    def get_user_image(self, account):
        if account.image:
            return account.image.url
        return settings.DEFAULT_MALE_IMG

    def to_representation(self, instance):
        ret                 = super().to_representation(instance)
        ret['reviewer']     = {
            "account_id":   instance.reviewer.id,
            "first_name":   instance.reviewer.user.first_name,
            "last_name":    instance.reviewer.user.last_name,
            "image":        self.get_user_image(instance.reviewer)
        }
        ret['created_at']   = instance.created_at.timestamp() * 1000
        return ret