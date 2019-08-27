from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED
from rest_framework.views import APIView
from apps.api.models import Notification
from apps.api.functions import authenticate

from .serializers import NotificationListSerializer

class NotificationListAPIView(APIView):
  renderer_classes = (JSONRenderer, )

  def get_objects(self, account):
    notifs = Notification.objects.filter(account = account)
    return notifs

  def get(self, request, *args, **kwargs):
    token   = request.META.get('HTTP_X_AUTH_TOKEN')
    account = authenticate(token)
    if account is not None:
      instance = self.get_objects(account)
      serializer = NotificationListSerializer(instance, many=True)
      return Response(serializer.data, status=HTTP_200_OK)
    return Response({}, status=HTTP_401_UNAUTHORIZED)

class UpdateNotificationAPIView(APIView):
  renderer_classes = (JSONRenderer, )

  def get_object(self, id, account):
    notifs = Notification.objects.filter(id = id, account = account)
    if notifs.exists():
      return notifs.first()
    return None

  def post(self, request, *args, **kwargs):
    token     = request.META.get('HTTP_X_AUTH_TOKEN')
    notif_id  = kwargs.get('id')
    account   = authenticate(token)
    if account is not None:
        notif = self.get_object(notif_id, account)
        if notif is not None:
          notif.read = True
          notif.save()
        return Response({'success': True}, status=HTTP_200_OK)
    return Response({}, status=HTTP_401_UNAUTHORIZED)