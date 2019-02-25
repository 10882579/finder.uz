from django.db.models import Q
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED
from rest_framework.views import APIView
from apps.api.models import ChatRoom
from apps.api.functions import authenticate

from .serializers import ConversationSerializer

class ConversationsAPIView(APIView):
    renderer_classes = (JSONRenderer, )

    def get_user_chats(self, account):
      instance = ChatRoom.objects.filter(
        Q(first = account) | 
        Q(second = account)
      )
      return instance

    def post(self, request, *args, **kwargs):
        token   = request.META.get('HTTP_X_AUTH_TOKEN')
        auth    = authenticate(token)
        if auth is not None:
          user_chats = self.get_user_chats(auth.account)
          serializer = ConversationSerializer(
            user_chats, 
            context={'account': auth.account}, 
            many=True
          )
          return Response(serializer.data, status=HTTP_200_OK)
        return Response({}, status=HTTP_401_UNAUTHORIZED)


    def get(self, request, *args, **kwargs):
        return Response({}, status=HTTP_400_BAD_REQUEST)