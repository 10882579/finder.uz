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
        account = authenticate(token)
        if account is not None:
            serializer = CreatePostSerializer(data = request.data, context={'account': account})
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

    def search_filter(self, search, params):

        posts = []
        re_state = params.get('state') if params.get('state') else r'([a-zA-Z]*)'
        re_category = params.get('category') if params.get('category') else r'([a-zA-Z]*)'
        re_condition = params.get('condition') if params.get('condition') else r'([a-zA-Z]*)'
        re_city_town = params.get('city_town') if params.get('city_town') else r'([a-zA-Z]*)'
        gte = params.get('gte') if params.get('gte') else 0
        lte = params.get('lte') if params.get('lte') else 2147483647

        for i in search:
            lst = Posts.objects.filter(
                title__contains=i,
                condition__regex=re_condition,
                city_town__regex=re_city_town,
                category__regex=re_category,
                price__range=(gte, lte),
                state__regex=re_state,
                posted = True,
                sold = False
            )
            for j in lst:
                posts.append(j)
        return list(set(posts))

    def get(self, request, *args, **kwargs):
        search = request.query_params.get('search')
        posts = Posts.objects.all().exclude(posted = False)
        
        if search:
            posts = self.search_filter(search, request.query_params)
            
        serializer = PostListSerializer(posts, many=True)
        return Response(serializer.data, status=HTTP_200_OK)

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


    def get(self, request, *args, **kwargs):
        token       = request.META.get('HTTP_X_AUTH_TOKEN')
        account     = authenticate(token)

        instance    = self.get_object(id = kwargs.get('id'))
        if instance is not None:
            data = PostByIdSerializer(instance).data
            if account is not None:
                data['saved'] = self.post_saved(account, instance)
                if account == instance.account:
                    data['posted'] = instance.posted
            return Response(data, status=HTTP_200_OK)
        return Response({}, status=HTTP_404_NOT_FOUND)

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
        account     = authenticate(token)

        if account is not None:
            context = {
                'post': self.get_object(account, **kwargs)
            }
            serializer = CreatePostSerializer(data = request.data, context = context)
            serializer.is_valid(raise_exception=False)
            if serializer.validated_data.get('errors') is None:
                self.get_object(account, **kwargs).update(serializer.validated_data)
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
        account     = authenticate(token)

        if account is not None:
            return self.save_or_delete_object(account, **kwargs)
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
        account     = authenticate(token)

        if account is not None:
            instance = self.get_object(account, **kwargs)
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
        account     = authenticate(token)

        if account is not None:
            instance = self.get_object(account, **kwargs)
            if instance is not None:
                self.delete_object_photos(instance.id)
                instance.delete()
                return Response({'updated': True}, status=HTTP_200_OK)
            return Response({}, status=HTTP_404_NOT_FOUND)
        return Response({}, status=HTTP_401_UNAUTHORIZED)

    def get(self, request, *args, **kwargs):
        return Response({}, status=HTTP_400_BAD_REQUEST)
