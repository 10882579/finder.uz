from django.conf import settings
from django.db.models import Q
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser

from apps.api.models import UserAccountFollowers, UserAccount, ChatRoom
from apps.api.account.serializers import *
from apps.api.functions import authenticate, get_user_account

class UserLoginAPIView(APIView):
    renderer_classes = (JSONRenderer,)

    def post(self, request, *args, **kwargs):
        serializer = UserLoginSerializer(data = request.data)
        if serializer.is_valid(raise_exception=True):
            account = serializer.validated_data['account']
            serializer = UserAccountSerializer(account)
            return Response(serializer.data, status=HTTP_200_OK)
        else:
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        return Response({}, status=HTTP_400_BAD_REQUEST)

class UserRegistrationAPIView(APIView):
    renderer_classes = (JSONRenderer, )

    def post(self, request, *args, **kwargs):
        user_serializer         = UserRegistrationSerializer(data = request.data)
        account_serializer      = AccountRegistrationSerializer(data = request.data)
        if user_serializer.is_valid(raise_exception = True) and account_serializer.is_valid(raise_exception = True):
            user        = user_serializer.create()
            account     = account_serializer.create(user = user)
            serializer  = UserAccountSerializer(account)
            return Response(serializer.data, status=HTTP_200_OK)
        return Response({}, status=HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        return Response({}, status=HTTP_400_BAD_REQUEST)

class UserAccountAPIView(APIView):
    renderer_classes    = (JSONRenderer, )

    def get(self, request, *args, **kwargs):
        token   = request.META.get('HTTP_X_AUTH_TOKEN')
        account = authenticate(token)
        if account is not None:
            serializer = UserAccountSerializer(account)
            return Response(serializer.data, status=HTTP_200_OK)
        return Response({}, status=HTTP_401_UNAUTHORIZED)

class UserAccountUpdateAPIView(APIView):
    renderer_classes    = (JSONRenderer, )

    def post(self, request, *args, **kwargs):
        token   = request.META.get('HTTP_X_AUTH_TOKEN')
        account = authenticate(token)

        if account is not None:
            serializer = UserAccountUpdateSerializer(data = request.data, context={'account': account})
            serializer.is_valid(raise_exception=False)
            if serializer.validated_data.get('errors'):
                return Response(serializer.validated_data['errors'], status=HTTP_400_BAD_REQUEST)
            else:
                serializer.save()
                return Response({'updated': True}, status=HTTP_200_OK)
        return Response({}, status=HTTP_401_UNAUTHORIZED)

class UserAccountByIdAPIView(APIView):
    renderer_classes    = (JSONRenderer, )

    def is_following(self, account, id):
        following = UserAccountFollowers.objects.filter(account = account, following = id)
        if following.exists():
            return True
        return False

    def get(self, request, *args, **kwargs):
        token           = request.META.get('HTTP_X_AUTH_TOKEN')
        account         = authenticate(token)
        account_by_id   = get_user_account(kwargs.get('id'))
        following       = False

        if account is not None:
            following = self.is_following(account = account, id = kwargs.get('id'))

        if account_by_id is not None:
            serializer = UserAccountByIdSerializer(account_by_id)
            return Response({'account': serializer.data,'following': following}, status=HTTP_200_OK)
        else:
            return Response({}, status=HTTP_404_NOT_FOUND)

class UserAccountFollowingsAPIView(APIView):
    renderer_classes    = (JSONRenderer, )

    def get_object(self, account, page):
        all_followers   = UserAccountFollowers.objects.filter(account=account)
        pages       = len(all_followers) // 20
        pages       = pages + 1 if len(all_followers) - (pages * 20) != 0 else pages

        if int(page) <= pages:
            frm = 0 if int(page) == 1 else (int(page) - 1) * 20 + 1
            till = frm + 20 if frm == 0 else frm + 19
            followers = all_followers[frm:till]
            return followers
        else:
            return []

        return False


    def get(self, request, *args, **kwargs):
        token       = request.META.get('HTTP_X_AUTH_TOKEN')
        page        = kwargs.get('page')
        account     = authenticate(token)

        if account is not None:
            data = self.get_object(account = account, page = page)
            if data is not False:
                serializer = UserAccountFollowingsSerializer(data, many=True)
                return Response(serializer.data, status=HTTP_200_OK)
            return Response({}, status=HTTP_400_BAD_REQUEST)
        return Response({}, status=HTTP_401_UNAUTHORIZED)

class UserAccountFollowAPIView(APIView):
    renderer_classes    = (JSONRenderer, )

    def create_or_delete_object(self, account, id):
        check = UserAccountFollowers.objects.filter(
            account = account,
            following = id
        )
        if check.exists():
            check.first().delete()
        else:
            UserAccountFollowers.objects.create(
                account = account,
                following = id
            )
        return True

    def post(self, request, *args, **kwargs):
        token   = request.META.get('HTTP_X_AUTH_TOKEN')
        id      = kwargs.get('id')
        account = authenticate(token)

        if account is not None:
            following_account = get_user_account(id)
            if following_account is not None and following_account.id != account.id:
                self.create_or_delete_object(account, following_account)
                return Response({'updated': True}, status=HTTP_200_OK)
            return Response({}, status=HTTP_404_NOT_FOUND)
        return Response({}, status=HTTP_401_UNAUTHORIZED)

    def get(self, request, *args, **kwargs):
        return Response({}, status=HTTP_400_BAD_REQUEST)

class UserPostListAPIView(APIView):
    renderer_classes = (JSONRenderer, )

    def get_object(self, account, **kwargs):
        id              = kwargs.get('id')
        page            = kwargs.get('page')
        all_posts       = Posts.objects.filter(account=id)

        if account is not None:
            if str(account.id) != str(id):
                all_posts = all_posts.filter(posted = True, sold = False)
        else:
            all_posts = all_posts.filter(posted = True, sold = False)

        pages       = len(all_posts) // 20
        pages       = pages + 1 if len(all_posts) - (pages * 20) != 0 else pages
        if int(page) <= pages:
            frm = 0 if int(page) == 1 else (int(page) - 1) * 20 + 1
            till = frm + 20 if frm == 0 else frm + 19
            posts = all_posts[frm:till]
            return posts

        return None

    def get(self, request, *args, **kwargs):
        token   = request.META.get('HTTP_X_AUTH_TOKEN')
        account = authenticate(token)
        data    = self.get_object(account, **kwargs)
        if data is not None:
            serializer = UserPostListSerializer(data, many=True)
            return Response(serializer.data, status=HTTP_200_OK)
        return Response([], status=HTTP_200_OK)

class UserSavedPostListAPIView(APIView):
    renderer_classes = (JSONRenderer, )

    def get_object(self, account, page):
        all_posts   = UserSavedPosts.objects.filter(account=account)
        pages       = len(all_posts) // 20
        pages       = pages + 1 if len(all_posts) - (pages * 20) != 0 else pages

        if int(page) <= pages:
            frm = 0 if int(page) == 1 else (int(page) - 1) * 20 + 1
            till = frm + 20 if frm == 0 else frm + 19
            posts = all_posts[frm:till]
            return posts

        return None

    def get(self, request, *args, **kwargs):
        token   = request.META.get('HTTP_X_AUTH_TOKEN')
        page    = kwargs.get('page')
        account = authenticate(token)
        if account is not None:
            data = self.get_object(account=account, page = page)
            if data is not None:
                serializer = UserSavedPostListSerializer(data, many=True)
                return Response(serializer.data, status=HTTP_200_OK)
            return Response([], status=HTTP_200_OK)
        return Response(status=HTTP_400_BAD_REQUEST)
