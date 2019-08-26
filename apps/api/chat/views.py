from django.db.models import Q
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED
from rest_framework.views import APIView
from apps.api.models import ChatRoom, Message, UserAccount
from apps.api.functions import authenticate, random_token, get_user_account

from .serializers import ConversationSerializer, MessageSerializer

import requests

class ChatRoomAPIView(APIView):
  renderer_classes = (JSONRenderer, )

  def get_chat_room(self, first, second):
    instance = ChatRoom.objects.filter(
      Q(first = first, second = second) | 
      Q(first = second, second = first)
    )
    if instance.exists():
      return instance.first().room
    else:
      room_name = random_token()
      ChatRoom.objects.create(
        room = room_name,
        first = first,
        second = second
      )
      return room_name

  def post(self, request, *args, **kwargs):
    token       = request.META.get('HTTP_X_AUTH_TOKEN')
    an_account  = get_user_account(kwargs.get('id'))
    account     = authenticate(token)

    if account != an_account and account is not None and an_account is not None:
      room = self.get_chat_room(account, an_account)
      return Response({"room": room}, status=HTTP_200_OK)
    return Response({}, status=HTTP_401_UNAUTHORIZED)

class ConversationsAPIView(APIView):
  renderer_classes = (JSONRenderer, )

  def get_user_chats(self, account):
    instance = ChatRoom.objects.filter(
      Q(first = account) | 
      Q(second = account)
    )
    return instance

  def get(self, request, *args, **kwargs):
    token   = request.META.get('HTTP_X_AUTH_TOKEN')
    account = authenticate(token)
    if account is not None:
      user_chats = self.get_user_chats(account)
      serializer = ConversationSerializer(
        user_chats, 
        context={'account': account}, 
        many=True
      )
      return Response(serializer.data, status=HTTP_200_OK)
    return Response({}, status=HTTP_401_UNAUTHORIZED)

class MessagesAPIView(APIView):
  renderer_classes = (JSONRenderer, )

  def get_chat(self, first, second):
    instance = ChatRoom.objects.filter(
      Q(first = first, second = second) | 
      Q(first = second, second = first)
    )
    if instance.exists():
      return instance.first()
    return None

  def get(self, request, *args, **kwargs):
    token   = request.META.get('HTTP_X_AUTH_TOKEN')
    account = authenticate(token)
    if account is not None:
      chat = self.get_chat(account, kwargs.get('id'))
      if chat is not None:
        instance = Message.objects.filter(room = chat)
        serializer = MessageSerializer(instance, many=True)
        return Response(serializer.data, status=HTTP_200_OK)
    return Response({}, status=HTTP_401_UNAUTHORIZED)

class SaveMessageAPIView(APIView):

  def get_chat(self, room):
    chat_room = ChatRoom.objects.filter(room = room)
    if chat_room.exists():
      return chat_room.first()
    return None
  
  def notify_user(self, token, data):
    url = os.environ.get('SOCKET_SERVER', 'http://localhost:3000')
    r = requests.post(url + '/notify/' + token + '/', data=data)


  def post(self, request, *args, **kwargs):
    token   = request.META.get('HTTP_X_AUTH_TOKEN')
    account = authenticate(token)
    message = request.data.get('message')
    room    = self.get_chat(kwargs.get('room'))

    if account is not None and room is not None and len(message) > 0:

      reciever  = room.first
      sender    = account

      if account == room.first:
        reciever  = room.second
        sender    = room.first
      self.notify_user(reciever.token, {"from": sender.id, "message": message, "chat_id": room.id})
      Message.objects.create(room = room, sender = sender, message = message)

      return Response({"success": True}, status=HTTP_200_OK)
    return Response({}, status=HTTP_401_UNAUTHORIZED)

  def get(self, request, *args, **kwargs):
    return Response({}, status=HTTP_400_BAD_REQUEST)