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

class CreateAccountReviewSerializer(ModelSerializer):

    class Meta:
        model = Review
        fields = [
            'rating',
            'review'
        ]

    def validate(self, data):

        rating = data.get('rating')
        review = data.get('review')

        if not rating and not len(review) > 0:
            data['error'] = 'Barcha ma\'lumotlarni kiriting!'

        return data

    def save(self):
        self.validated_data['reviewer'] = self.context.get('reviewer')
        self.validated_data['reviewee'] = self.context.get('reviewee')
        
        Review.objects.create(**self.validated_data)


