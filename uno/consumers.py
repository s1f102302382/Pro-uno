import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

'''
# digit // 
red = 0, bule = 1, yellow = 2, green = 3

# function card // 
skip = 50, reverse = 55, change_color = 60, fullcolor = 70, draw4 = 99
'''

Deck = [1, 2, 3, 4, 5, 6, 7, 8, 9,
        11, 12, 13, 14, 15, 16, 17, 18, 19,
        21, 22, 23, 24, 25, 26, 27, 28, 29,
        31, 32, 33, 34, 35, 36, 37, 33, 39,
        50, 150, 250, 350,
        55, 155, 255, 355,
        60, 160, 260, 360,
        70, 170, 270, 370,
        99, 199, 299, 399,
        ]
class ChatConsumer(WebsocketConsumer):
    Deck = [1, 2, 3, 4, 5, 6, 7, 8, 9,
        11, 12, 13, 14, 15, 16, 17, 18, 19,
        21, 22, 23, 24, 25, 26, 27, 28, 29,
        31, 32, 33, 34, 35, 36, 37, 33, 39,
        50, 150, 250, 350,
        55, 155, 255, 355,
        60, 160, 260, 360,
        70, 170, 270, 370,
        99, 199, 299, 399,
        ]
    
    

    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "uno_%s" % self.room_name
        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        # leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        # Send message to room group
        #self.send(text_data=json.dumps({"message": message}))
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {"type": ""}
        )

    def game_update(self, event):
        message = event['message']
        print('game_update-message', message)
        self.send(text_data=message)
