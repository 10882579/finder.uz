from django.db.models import Q
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED
from rest_framework.views import APIView
from apps.api.models import ChatRoom, Message
from apps.api.functions import authenticate

from .serializers import ConversationSerializer, MessageSerializer

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

class MessagesAPIView(APIView):
  renderer_classes = (JSONRenderer, )

  def get_user_chat(self, account, sec_account):
    instance = ChatRoom.objects.filter(
      Q(first = account, second = sec_account) | 
      Q(first = sec_account, second = account)
    )
    if instance.exists():
      return instance.first()
    return None

  def post(self, request, *args, **kwargs):
    token   = request.META.get('HTTP_X_AUTH_TOKEN')
    auth    = authenticate(token)
    if auth is not None:
      chat = self.get_user_chat(auth.account, kwargs.get('id'))
      if chat is not None:
        instance = Message.objects.filter(room = chat)
        serializer = MessageSerializer(instance, many=True)
        return Response(serializer.data, status=HTTP_200_OK)
    return Response({}, status=HTTP_401_UNAUTHORIZED)

  def get(self, request, *args, **kwargs):
    return Response({}, status=HTTP_400_BAD_REQUEST)