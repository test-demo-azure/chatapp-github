from .models import Message

from django.contrib.auth import get_user_model

import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from .views import last_15_messages, get_user_contact, get_current_chat

User= get_user_model()

class ChatConsumer(WebsocketConsumer):

    def fetch_messages(self, data):
        messages= last_15_messages(data["chatID"])
        # print(data["chatID"])
        content= {
            'command': 'messages',
            'messages': self.messages_to_json(messages)
        }

        # print(len(content['messages']))


        self.send_message(content)
    
    def messages_to_json(self, messages):
        result= []

        for message in messages:
            result.append(self.message_to_json(message))
        
        return result

    def message_to_json(self, message):
        return {
            'id': message.id,
            'author': message.contact.user.username,
            'content': message.content,
            'timestamp': str(message.timestamp)
        }

    def new_message(self, data):
        user_contact= get_user_contact(data['from'])
        # print(data['message'])
        # author_user= User.objects.get(username=author)
        message= Message.objects.create(
            contact= user_contact,
            content= data['message']
        )
        # print(data)
        current_chat= get_current_chat(data['chatID'])
        current_chat.messages.add(message)
        current_chat.save()
        content= {
            'command': 'new_message',
            'message': self.message_to_json(message)
        }

        return self.send_chat_message(content)

    commands = {
        'fetch_messages': fetch_messages,
        'new_message': new_message
    }

    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "chat_%s" % self.room_name

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )

        self.accept()
    
    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        # print("First: ")
        # print(text_data_json)
        self.commands[text_data_json['command']](self, text_data_json)

    def send_chat_message(self, message):
        # message = text_data_json["message"]

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {"type": "chat_message", 
                                   "message": message}
        )
    
    def send_message(self, message):
        text_data=json.dumps(message)
        self.send(text_data)

    def chat_message(self, event):
        message = event["message"]
        # print(event)
        # Send message to WebSocket
        async_to_sync(self.send(text_data=json.dumps(message)))

