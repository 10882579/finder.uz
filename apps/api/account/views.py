from django.conf import settings
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser

from apps.api.models import Sessions, UserAccountFollowers, UserAccount
from apps.api.account.serializers import *
from apps.api.functions import random_token, authenticate

class UserLoginAPIView(APIView):
    renderer_classes = (JSONRenderer, )

    def get_authentication_token(self, account):
        token = random_token()
        all_sessions = Sessions.objects.filter(account = account)
        for s in all_sessions:
            s.delete()

        Sessions.objects.create(
            account     = account,
            token       = token,
            on_session  = True
        )
        return token

    def post(self, request, *args, **kwargs):
        serializer = UserLoginSerializer(data = request.data)
        if serializer.is_valid(raise_exception=False):
            errors = serializer.validated_data.get('errors')
            if errors is None:
                token = self.get_authentication_token(account = serializer.validated_data['account'])
                return Response({'token': token}, status=HTTP_200_OK)
            elif errors is not None:
                return Response(serializer.validated_data['errors'], status=HTTP_400_BAD_REQUEST)

        return Response({}, status=HTTP_401_UNAUTHORIZED)

    def get(self, request, *args, **kwargs):
        return Response({}, status=HTTP_400_BAD_REQUEST)

class UserRegistrationAPIView(APIView):
    renderer_classes = (JSONRenderer, )

    def get_authentication_token(self, account):
        token = random_token()
        Sessions.objects.create(
            account     = account,
            token       = token,
            on_session  = True
        )
        return token

    def post(self, request, *args, **kwargs):
        serializer = UserRegistrationSerializer(data = request.data)
        serializer.is_valid(raise_exception = False)
        errors = serializer.validated_data.get('errors')
        if errors is None:
            account = serializer.create()
            if account is not None:
                token = self.get_authentication_token(account)
                return Response({'token': token}, status=HTTP_200_OK)
            return Response({}, status=HTTP_401_UNAUTHORIZED)
        elif errors is not None:
            return Response(errors, status=HTTP_400_BAD_REQUEST)

        return Response({}, status=HTTP_401_UNAUTHORIZED)

    def get(self, request, *args, **kwargs):
        return Response({}, status=HTTP_400_BAD_REQUEST)

class UserAccountAPIView(APIView):
    renderer_classes    = (JSONRenderer, )

    def post(self, request, *args, **kwargs):
        token   = request.META.get('HTTP_X_AUTH_TOKEN')
        auth    = authenticate(token)
        if auth is not None:
            serializer = UserAccountSerializer(auth.account)
            return Response(serializer.data, status=HTTP_200_OK)
        return Response({}, status=HTTP_401_UNAUTHORIZED)

    def get(self, request, *args, **kwargs):
        return Response({}, status=HTTP_400_BAD_REQUEST)

class UserAccountUpdateAPIView(APIView):
    # parser_classes      = (MultiPartParser, FormParser)
    renderer_classes    = (JSONRenderer, )

    def post(self, request, *args, **kwargs):
        token  = request.META.get('HTTP_X_AUTH_TOKEN')
        auth   = authenticate(token)

        if auth is not None:
            serializer = UserAccountUpdateSerializer(data = request.data, context={'account': auth.account})
            serializer.is_valid(raise_exception=False)
            if serializer.validated_data.get('errors'):
                return Response(serializer.validated_data['errors'], status=HTTP_400_BAD_REQUEST)
            else:
                serializer.save()
                return Response({'updated': True}, status=HTTP_200_OK)
        return Response({}, status=HTTP_401_UNAUTHORIZED)

class UserAccountByIdAPIView(APIView):
    renderer_classes    = (JSONRenderer, )

    def user_following(self, account, id):
        account = UserAccountFollowers.objects.filter(account = account, following = id)
        if account.exists():
            return True
        return False

    def get_object(self, id):
        account = UserAccount.objects.filter(id = id)
        if account.exists():
            return account.first()
        return None

    def post(self, request, *args, **kwargs):
        token       = request.META.get('HTTP_X_AUTH_TOKEN')
        id          = kwargs.get('id')
        following   = False

        auth        = authenticate(token)
        serializer  = UserAccountByIdSerializer(self.get_object(id))

        if self.get_object(id) is None:
            return Response({}, status=HTTP_404_NOT_FOUND)

        if auth is not None:
            following = self.user_following(account = auth.account, id = id)

        return Response({'account': serializer.data,'following': following}, status=HTTP_200_OK)

    def get(self, request, *args, **kwargs):
        return Response({}, status=HTTP_400_BAD_REQUEST)

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


    def post(self, request, *args, **kwargs):
        token       = request.META.get('HTTP_X_AUTH_TOKEN')
        page        = kwargs.get('page')
        auth        = authenticate(token)

        if auth is not None:
            data = self.get_object(account = auth.account, page = page)
            if data is not False:
                serializer = UserAccountFollowingsSerializer(data, many=True)
                return Response(serializer.data, status=HTTP_200_OK)
            return Response({}, status=HTTP_400_BAD_REQUEST)
        return Response({}, status=HTTP_401_UNAUTHORIZED)

    def get(self, request, *args, **kwargs):
        return Response({}, status=HTTP_400_BAD_REQUEST)

class UserAccountFollowAPIView(APIView):
    renderer_classes    = (JSONRenderer, )

    def get_object(self, id):
        account = UserAccount.objects.filter(id = id)
        if account.exists():
            return account.first()

        return None

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
        auth    = authenticate(token)

        if auth is not None:
            account = self.get_object(id)
            if account is not None and account.id != auth.account.id:
                self.create_or_delete_object(auth.account, account)
                return Response({'updated': True}, status=HTTP_200_OK)
            return Response({}, status=HTTP_404_NOT_FOUND)
        return Response({}, status=HTTP_401_UNAUTHORIZED)

    def get(self, request, *args, **kwargs):
        return Response({}, status=HTTP_400_BAD_REQUEST)

class UserPostListAPIView(APIView):
    renderer_classes = (JSONRenderer, )

    def get_object(self, auth, **kwargs):
        id              = kwargs.get('id')
        page            = kwargs.get('page')
        all_posts       = Posts.objects.filter(account=id)

        if auth is not None:
            if str(auth.account.id) != str(id):
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

    def post(self, request, *args, **kwargs):
        token   = request.META.get('HTTP_X_AUTH_TOKEN')
        auth    = authenticate(token)
        data    = self.get_object(auth, **kwargs)
        if data is not None:
            serializer = UserPostListSerializer(data, many=True)
            return Response(serializer.data, status=HTTP_200_OK)
        return Response([], status=HTTP_200_OK)

    def get(self, request, *args, **kwargs):
        return Response({}, status=HTTP_400_BAD_REQUEST)

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

    def post(self, request, *args, **kwargs):
        token   = request.META.get('HTTP_X_AUTH_TOKEN')
        page    = kwargs.get('page')
        auth    = authenticate(token)
        if auth is not None:
            data = self.get_object(account=auth.account, page = page)
            if data is not None:
                serializer = UserSavedPostListSerializer(data, many=True)
                return Response(serializer.data, status=HTTP_200_OK)
            return Response([], status=HTTP_200_OK)
        return Response(status=HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        return Response({}, status=HTTP_400_BAD_REQUEST)
