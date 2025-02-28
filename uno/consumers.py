import json, random
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

'''
# digit // 
red = 0, bule = 1, yellow = 2, green = 3

# function card // 
skip = 40, reverse = 50, draw2 = 60, play_all_same_color = 70, change_color = 80, draw4 = 90
'''

class UNOConsumer(WebsocketConsumer):
    number_of_initial_deck = 7
    NUMBER_OF_number_card = 10  # 0~9
    COLOR = [0, 1, 2, 3]        # red, bule, yellow, green
    FUNCTION_CARD = {40: "skip", 50: "reverse", 60: "draw2", 70: "play_all_same_color"}
    COLOR_CHANGE = {80: "change_color", 90: "draw4"}

    # color
    #red = 0, bule = 1, yellow = 2, green = 3
    # function card
    #skip = 40, reverse = 50, draw2 = 60, play_all_same_color = 70, change_color = 80, draw4 = 90
    
    def create_initial_deck(self, number):
        '''
        self.Deck = [1, 2, 3, 4, 5, 6, 7, 8, 9,
        11, 12, 13, 14, 15, 16, 17, 18, 19,
        21, 22, 23, 24, 25, 26, 27, 28, 29,
        31, 32, 33, 34, 35, 36, 37, 33, 39,
        50, 150, 250, 350,
        55, 155, 255, 355,
        60, 160, 260, 360,
        70, 170, 270, 370,
        99, 199, 299, 399,
        ]
        '''
        deck = [i + c * 10 for c in self.COLOR for i in range(0, 10)]
        deck += [i * 100 + F for i in range(0, len(self.COLOR)) for F in self.FUNCTION_CARD]
        deck += self.COLOR_CHANGE
        random.shuffle(deck)
        return random.sample(deck, k=number)
    '''
    def played_card(self, card):
        # function card
        skip = 50, reverse = 55, change_color = 60,
        fullcolor = 70, draw4 = 99

        if card == skip:
            pass
        elif card == reverse:
            pass
        elif card == change_color:
            pass
        elif card == fullcolor:
            pass
        elif card == draw4:
            pass
        return []
    '''

    def is_valid_play(self, card):
        top_card = self.discard_pile[-1]
        
        # 先に数字カードの判定をします
        is_both_number = (card < 40 & top_card < 40)

        # もし数字であれば40より小さいので10で割った商で色を選択判別できる
        if (is_both_number ==  True):
            is_same_color = (card // 10 == top_card // 10)
            is_same_number = (card % 10 == top_card % 10)
            return (is_same_color or is_same_number) == True
        elif (card >= 40 and top_card < 40): 
            # 前の方のカードが数字で自分のカードは数字じゃない場合
            # -> 同じ色かまたは色を変えれるカードか
            is_same_color = (card // 100 == top_card // 10)
            is_card_change_color = (card in self.COLOR_CHANGE)
            return (is_same_color or is_card_change_color) == True
        elif (card < 40 and top_card >= 40):
            # 前のカードは特別カードで自分のカードは数字カードの場合
            # -> 同じ色
            is_same_color = (card // 10 and top_card // 100)
            return (is_same_color) == True
        #elif (card >= 40 and top_card >= 40):
        else:
            # 前のカードも今出したカードも特別カードである場合
            # -> 同じ特別カードかまたは色を変えれるカードか
            is_same_function_card = (card % 100 == top_card % 100)
            is_card_change_color = (card in self.COLOR_CHANGE)
            return (is_same_function_card or is_card_change_color) == True

    def draw_n(self, n):
        self.draw += n

    def apply_card_play(self, card):
        if (card in self.FUNCTION_CARD.key()):
            effect = self.FUNCTION_CARD[card]
        elif(card in self.COLOR_CHANGE.key()):
            effect = self.COLOR_CHANGE[card]
        else:
            # 数字カードの場合は何も効果がない
            effect = "None"
        
        return self.next_turn(self, effect)
    
    def next_turn(self, effect):
        if (effect == "skip"):
            self.current_turn = (self.current_turn + self.direction * 2) % len(self.players)
        elif (effect == "reverse"):
            self.direction *= -1
            self.current_turn = (self.current_turn + self.direction) % len(self.players)
        elif (effect == "draw2"):
            self.draw_n(self, 2)
            self.current_turn = (self.current_turn + self.direction) % len(self.players)
        elif (effect == "play_all_same_color"):
            pass
            # ここで全て同じ色のカードを出す
            self.current_turn = (self.current_turn + self.direction) % len(self.players)
        elif (effect == "change_color"):
            self.current_turn = (self.current_turn + self.direction) % len(self.players)
        elif (effect == "draw4"):
            self.draw_n(self, 4)
            self.current_turn = (self.current_turn + self.direction) % len(self.players)
    
    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "uno_%s" % self.room_name
        self.players = {}       # プレイヤーの管理
        self.hands = {}         # プレイヤーごとの手札管理
        self.deck = self.create_initial_deck(40) # 山札
        self.discard_pile = [self.deck.pop()]
        self.current_turn = 0   # 現在のターン
        self.direction = 1      # 進行方向　時計回りだと１，反時計回りだと-1
        self.draw = 0
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
        data = json.loads(text_data)
        action = data.get("action")
        player = data.get("player")

        if action == "join":
            print("プレイヤーが接続しました")
            self.hands[player] = self.create_initial_deck(self.number_of_initial_deck)
            # self.hands -> {playername: [cardlist]}

            self.players[player] = {"hand": self.hands[player]}
            # self.players -> {playername: {"hand": [card]}}
        elif action == "play_card":
            card = data.get("card")
            if self.is_valid_play(card):
                self.hands[player].remove(card)
                self.discard_pile.append(card)
                self.apply_card_play(card)
            self.send_game_update(player)

    def send_game_update(self, cuurent_player=None):
        masked_player = {}
        for player_name in self.players:
            if player_name == cuurent_player:
                masked_player[player_name] = self.players[player_name]
            else:
                masked_player[player_name] = len(self.players[player_name])
        
        update = {
            "turn": self.current_turn,
            "player": masked_player,
            "top_card": self.discard_pile[-1],
        }
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {"type": "game_update", "message": json.dumps(update)}
        )

    def game_update(self, event):
        message = event['message']
        print('game_update-message', message)
        self.send(text_data=message)
