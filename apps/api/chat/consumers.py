from asgiref.sync import async_to_sync
from apps.api.functions import authenticate
from apps.api.models import UserAccount, ChatRoom, Message
from channels.generic.websocket import WebsocketConsumer
from django.db.models import Q
from django.conf import settings

import json

class ChatConsumer(WebsocketConsumer):

	def get_room_name(self, account, receiver):
		chat_room = ChatRoom.objects.filter( 
			Q(first = account, second = receiver) |
			Q(first = receiver, second = account)
		)

		if chat_room.exists():
			self.chat_room_query = chat_room.first()
			return self.chat_room_query.room
		return None

	def valid_chat(self):
		self.token = self.scope['url_route']['kwargs']['token']
		self.receiver_id = self.scope['url_route']['kwargs']['id']
		self.auth = authenticate(self.token)

		receiver = UserAccount.objects.filter(id = self.receiver_id)

		if self.auth is not None and receiver.exists() and self.auth.account != receiver.first():
			self.room_name = self.get_room_name(self.auth.account, receiver.first())
			if self.room_name is not None:
				self.receiver = receiver.first()
				self.account = self.auth.account
				self.user = self.account.user
				return True
		
		return False

	def get_user_image(self, obj):
		if obj.sender.image:
			return obj.sender.image.url
		else:
			return settings.DEFAULT_MALE_IMG

	def connect(self):
		if self.valid_chat():

			async_to_sync(self.channel_layer.group_add)(
				self.room_name,
				self.channel_name
			)

			self.accept()

	def receive(self, text_data):
		text_data_json = json.loads(text_data)

		message_obj = Message.objects.create(
			room = self.chat_room_query,
			sender = self.account,
			message = text_data_json['message']
		)

		data = {
			'account_id': message_obj.sender.id,
			'first_name': message_obj.sender.user.first_name,
			'last_name': message_obj.sender.user.last_name,
			'image': self.get_user_image(message_obj),
			'message': message_obj.message,
			'created_at': message_obj.created_at.timestamp() * 1000
		}

		async_to_sync(self.channel_layer.group_send)(
			self.room_name,
			{
				'type': 'send_message',
				'data': data
			}
		)

	def send_message(self, event):
		self.send(text_data=json.dumps(event['data']))

	def disconnect(self, close_code):
		self.close()