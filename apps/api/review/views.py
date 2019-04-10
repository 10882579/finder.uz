from django.conf import settings
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND
from rest_framework.views import APIView

from apps.api.models import Review, UserAccount
from apps.api.review.serializers import AccountReviewsSerializer, CreateAccountReviewSerializer
from apps.api.functions import authenticate

class AccountReviewsAPIView(APIView):

    def get_object(self, account):
        return Review.objects.filter(reviewee = account)

    def post(self, request, *args, **kwargs):
        token   = request.META.get('HTTP_X_AUTH_TOKEN')
        auth    = authenticate(token)
        if auth is not None:
            serializer = AccountReviewsSerializer(data = self.get_object(auth.account), many=True)
            serializer.is_valid(raise_exception=False)
            return Response(serializer.data, status=HTTP_200_OK)
        return Response({}, status=HTTP_401_UNAUTHORIZED)

    def get(self, request, *args, **kwargs):
        return Response({}, status=HTTP_400_BAD_REQUEST)

class AccountReviewsByIdAPIView(APIView):

    def get_object(self, account):
        return Review.objects.filter(reviewee = account)

    def post(self, request, *args, **kwargs):
        token   = request.META.get('HTTP_X_AUTH_TOKEN')
        auth    = authenticate(token)
        if auth is not None:
            data = self.get_object(kwargs.get('id'))
            serializer = AccountReviewsSerializer(data = data, many=True)
            serializer.is_valid(raise_exception=False)
            return Response(serializer.data, status=HTTP_200_OK)
        return Response({}, status=HTTP_401_UNAUTHORIZED)

    def get(self, request, *args, **kwargs):
        return Response({}, status=HTTP_400_BAD_REQUEST)

class CreateAccountReviewAPIView(APIView):

    def authorize_account(self, id):
        account  = UserAccount.objects.filter(id = id)

        if account.exists():
            return account.first()

        return None

    def post(self, request, *args, **kwargs):
        token       = request.META.get('HTTP_X_AUTH_TOKEN')
        auth        = authenticate(token)
        reviewee    = self.authorize_account(kwargs.get('id'))
        
        if auth is not None and reviewee is not None:
            serializer = CreateAccountReviewSerializer(
                data = request.data, 
                context={
                    "reviewer": auth.account,
                    "reviewee": reviewee
                }
            )
            serializer.is_valid(raise_exception=False)
            if serializer.validated_data.get('errors') is None:
                serializer.save()
            return Response({}, status=HTTP_200_OK)
        return Response({}, status=HTTP_401_UNAUTHORIZED)

    def get(self, request, *args, **kwargs):
        return Response({}, status=HTTP_400_BAD_REQUEST)