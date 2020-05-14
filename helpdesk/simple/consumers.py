import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


# synchronous WebSocket consumer
class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']  # see ./routing.py:6
        self.room_group_name = f'chat_{self.room_name}'

        # The async_to_sync(…) wrapper is required because ChatConsumer is a synchronous WebsocketConsumer but it is
        # calling an asynchronous channel layer method. (All channel layer methods are asynchronous.)
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )

        # Accepts the WebSocket connection.
        # If you do not call accept() within the connect() method then the connection will be rejected and closed.
        #   You might want to reject a connection for example because the requesting user is not authorized to perform
        #   the requested action.
        # It is recommended that accept() be called as the last action in connect() if you choose to accept the
        #   connection.
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    def receive(self, text_data=None, bytes_data=None):
        json_data = json.loads(text_data)
        message = json_data['message']

        # self.send(text_data=json.dumps({
        #     'message': f'[echo] {message}',  # echo back the message to the client
        # }))

        # send message to room_group
        # An event has a special 'type' key corresponding to the name of the method that should be invoked on
        #   consumers that receive the event.
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {
                'type': 'chat_message',
                'message': message,
            }
        )

    def chat_message(self, event):
        message = event['message']

        # send message to WebSocket
        self.send(text_data=json.dumps({
            'message': f'[{self.room_name}] {message}'
        }))