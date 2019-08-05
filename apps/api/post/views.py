from django.conf import settings
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser

from apps.api.models import UserSavedPosts, Posts
from apps.api.post.serializers import *
from apps.api.functions import authenticate

class CreatePostAPIView(APIView):
    renderer_classes    = (JSONRenderer, )
    # parser_classes      = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        token   = request.META.get('HTTP_X_AUTH_TOKEN')
        auth    = authenticate(token)
        if auth is not None:
            serializer = CreatePostSerializer(data = request.data, context={'account': auth.account})
            serializer.is_valid(raise_exception=False)
            if serializer.validated_data.get('errors') is None:
                serializer.save()
                return Response({'uploaded': True}, status=HTTP_200_OK)
            return Response(serializer.validated_data.get('errors'), status=HTTP_400_BAD_REQUEST)
        return Response({}, status=HTTP_401_UNAUTHORIZED)

    def get(self, request, *args, **kwargs):
        return Response({}, status=HTTP_400_BAD_REQUEST)

class PostListAPIView(APIView):
    renderer_classes = (JSONRenderer, )

    def get_posts(self, premium):
        return Posts.objects.filter(
            premium = premium,
            posted = True,
            sold = False
        ).order_by('-created_at')

    def post(self, request, *args, **kwargs):
        premium = PostListSerializer(self.get_posts(premium = True), many=True)
        regular = PostListSerializer(self.get_posts(premium = False), many=True)
        return Response({
                            'premium': premium.data,
                            'regular': regular.data
                        }, status=HTTP_200_OK)

    def get(self, request, *args, **kwargs):
        return Response({}, status=HTTP_400_BAD_REQUEST)

class PostByIdAPIView(APIView):
    renderer_classes = (JSONRenderer, )

    def get_object(self, id):
        object = Posts.objects.filter(id = id)
        if object.exists():
            return object.first()
        return None

    def post_saved(self, account, instance):
        saved = UserSavedPosts.objects.filter(account = account, post = instance.id)
        if saved.exists():
            return True
        return False


    def post(self, request, *args, **kwargs):
        token       = request.META.get('HTTP_X_AUTH_TOKEN')
        auth        = authenticate(token)

        instance    = self.get_object(id = kwargs.get('id'))
        if instance is not None:
            data = PostByIdSerializer(instance).data
            if auth is not None:
                data['saved'] = self.post_saved(auth.account, instance)
                if auth.account == instance.account:
                    data['posted'] = instance.posted
            return Response(data, status=HTTP_200_OK)
        return Response({}, status=HTTP_404_NOT_FOUND)

    def get(self, request, *args, **kwargs):
        return Response({}, status=HTTP_400_BAD_REQUEST)

class EditPostByIdAPIView(APIView):
    renderer_classes = (JSONRenderer, )

    def get_object(self, account, **kwargs):
        id          = kwargs.get('id')
        post        = Posts.objects.filter(account=account, id=id)
        if post.exists():
            return post.first()
        return None

    def post(self, request, *args, **kwargs):
        token       = request.META.get('HTTP_X_AUTH_TOKEN')
        auth        = authenticate(token)

        if auth is not None:
            context = {
                'post': self.get_object(auth.account, **kwargs)
            }
            serializer = CreatePostSerializer(data = request.data, context = context)
            serializer.is_valid(raise_exception=False)
            if serializer.validated_data.get('errors') is None:
                self.get_object(auth.account, **kwargs).update(serializer.validated_data)
                serializer.update()
                return Response({'uploaded': True}, status=HTTP_200_OK)
            return Response(serializer.validated_data.get('errors'), status=HTTP_400_BAD_REQUEST)
        return Response({}, status=HTTP_401_UNAUTHORIZED)

    def get(self, request, *args, **kwargs):
        return Response({}, status=HTTP_400_BAD_REQUEST)

class SavePostByIdAPIView(APIView):
    renderer_classes = (JSONRenderer, )

    def create_object(self, account, **kwargs):
        instance = Posts.objects.filter(id = kwargs['id'])
        if instance.exists():
            UserSavedPosts.objects.create(
                account     = account,
                post        = instance.first()
            )
            return Response({'updated': True}, status=HTTP_200_OK)
        return Response({}, status=HTTP_404_NOT_FOUND)

    def save_or_delete_object(self, account, **kwargs):
        instance = UserSavedPosts.objects.filter(post = kwargs['id'], account = account)
        if instance.exists():
            instance.first().delete()
            return Response({'updated': True}, status=HTTP_200_OK)
        else:
            return self.create_object(account, **kwargs)

    def post(self, request, *args, **kwargs):
        token       = request.META.get('HTTP_X_AUTH_TOKEN')
        auth        = authenticate(token)

        if auth is not None:
            return self.save_or_delete_object(auth.account, **kwargs)
        return Response({}, status=HTTP_401_UNAUTHORIZED)

    def get(self, request, *args, **kwargs):
        return Response({}, status=HTTP_400_BAD_REQUEST)

class SoldPostByIdAPIView(APIView):
    renderer_classes = (JSONRenderer, )

    def get_object(self, account, **kwargs):
        instance = Posts.objects.filter(account=account, id=kwargs['id'])
        if instance.exists():
            return instance.first()
        return None

    def post(self, request, *args, **kwargs):
        token       = request.META.get('HTTP_X_AUTH_TOKEN')
        auth        = authenticate(token)

        if auth is not None:
            instance = self.get_object(auth.account, **kwargs)
            if instance is not None:
                instance.update_sold()
                return Response({'updated': True}, status=HTTP_200_OK)
            return Response({}, status=HTTP_404_NOT_FOUND)
        return Response({}, status=HTTP_401_UNAUTHORIZED)

    def get(self, request, *args, **kwargs):
        return Response({}, status=HTTP_400_BAD_REQUEST)

class DeletePostByIdAPIView(APIView):
    renderer_classes = (JSONRenderer, )

    def delete_object_photos(self, id):
        photos = PostPhotos.objects.filter(post=id)
        for photo in photos:
            photo.image.delete()
            photo.delete()


    def get_object(self, account, **kwargs):
        instance = Posts.objects.filter(account=account, id=kwargs['id'])
        if instance.exists():
            return instance.first()
        return None


    def post(self, request, *args, **kwargs):
        token       = request.META.get('HTTP_X_AUTH_TOKEN')
        auth        = authenticate(token)

        if auth is not None:
            instance = self.get_object(auth.account, **kwargs)
            if instance is not None:
                self.delete_object_photos(instance.id)
                instance.delete()
                return Response({'updated': True}, status=HTTP_200_OK)
            return Response({}, status=HTTP_404_NOT_FOUND)
        return Response({}, status=HTTP_401_UNAUTHORIZED)

    def get(self, request, *args, **kwargs):
        return Response({}, status=HTTP_400_BAD_REQUEST)
