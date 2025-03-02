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

    players = {}       # プレイヤーの管理：手札などを含めて
    players_turn = []
    hands = {}         # プレイヤーごとの手札管理
    deck = []          # 山札
    discard_pile = []  # 捨て札の山
    current_turn = 0   # 現在のターン
    direction = 1      # 進行方向　時計回りだと１，反時計回りだと-1
    draw = 0
    # color
    # red = 0, bule = 1, yellow = 2, green = 3
    # function card
    # skip = 40, reverse = 50, draw2 = 60, play_all_same_color = 70, change_color = 80, draw4 = 90
    
    def create_initial_deck(self, number):
        deck = [i + c * 10 for c in self.COLOR for i in range(0, 10)]
        deck += [i * 100 + F for i in range(0, len(self.COLOR)) for F in self.FUNCTION_CARD]
        deck += self.COLOR_CHANGE
        random.shuffle(deck)
        return random.sample(deck, k=number)

    def is_valid_play(self, card):
        print("is_valid_play に飛びました")
        top_card = self.discard_pile[-1]
        print("現在の捨札の一番上は", top_card)
        # 先に数字カードの判定をします
        is_both_number = (card < 40 and top_card < 40)

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
        if (card in self.FUNCTION_CARD.keys()):
            effect = self.FUNCTION_CARD[card]
            print("機能カードです")
        elif(card in self.COLOR_CHANGE.keys()):
            effect = self.COLOR_CHANGE[card]
            print("色を変更できるカードです")
        else:
            # 数字カードの場合は何も効果がない
            effect = "None"
        
        return self.next_turn(effect)
    
    def next_turn(self, effect):
        print("next_turn関数に飛びました!")
        if (effect == "skip"):
            print("skipカードが出されました")
            self.current_turn = (self.current_turn + self.direction * 2) % len(self.players)
        elif (effect == "reverse"):
            print("reverseカードが出されました")
            self.direction *= -1
            self.current_turn = (self.current_turn + self.direction) % len(self.players)
        elif (effect == "draw2"):
            print("draw2カードが出されました\nまだdraw関数が完成されていませんので実装を楽しみに待ってください")
            #self.draw_n(self, 2)
            self.current_turn = (self.current_turn + self.direction) % len(self.players)
        elif (effect == "play_all_same_color"):
            print("play_all_same_colorカードが出されました")
            pass
            # ここで全て同じ色のカードを出す
            self.current_turn = (self.current_turn + self.direction) % len(self.players)
        elif (effect == "change_color"):
            print("change_colorカードが出されました")
            self.current_turn = (self.current_turn + self.direction) % len(self.players)
        elif (effect == "draw4"):
            print("draw4カードが出されました")
            #self.draw_n(self, 4)
            self.current_turn = (self.current_turn + self.direction) % len(self.players)
        else:
            # 何もなければ数字カードです
            print("数字カードのため通常進行します")
            self.current_turn = (self.current_turn + self.direction) % len(self.players)
        
        #return self.players_turn[self.current_turn]

    
    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "uno_%s" % self.room_name

        if not UNOConsumer.players:     # 最初のプレイヤーが接続したときにののみ初期化
            #UNOConsumer.players_turn.append()
            UNOConsumer.deck = self.create_initial_deck(40)
            UNOConsumer.discard_pile = [UNOConsumer.deck.pop()]
            UNOConsumer.current_turn = 0
            UNOConsumer.direction = 1
            UNOConsumer.draw = 0
        # Join room group
        else:
            print("既存のプレイヤーデータを維持する")

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
        print("現在のカードを出したプレイヤーは", player)
        if action == "join":
            if player not in self.players:
                print(player, "が接続しました")
                self.hands[player] = self.create_initial_deck(self.number_of_initial_deck)
                # self.hands -> {playername: [cardlist]}

                self.players[player] = {"hand": self.hands[player]}
                # self.players -> {playername: {"hand": [card]}}

                # ここでプレイヤーの名前が players_turnに追加
                if player not in self.players_turn:
                    self.players_turn.append(player)
            else:
                print(player, "はすでに存在しています")

            print("self.player:", self.players)
            print("self.players_turn", self.players_turn)
            print("self.hands:", self.hands)
            print("self.deck:", self.deck)
            print("self.discard_pile", self.discard_pile)
            print("self.current_turn:", self.current_turn)
            print("self.direction:", self.direction)
            print("self.draw:", self.draw)
            """
            self.players = {}       # プレイヤーの管理
            self.hands = {}         # プレイヤーごとの手札管理
            self.deck = self.create_initial_deck(40) # 山札
            self.discard_pile = [self.deck.pop()]
            self.current_turn = 0   # 現在のターン
            self.direction = 1      # 進行方向  時計回りだと１，反時計回りだと-1
            self.draw= 0
            """
            self.send_game_update(player)
        elif action == "play_card":
            # print("カードを受け取りました！")
            card = data.get("card")
            print("このカードを受け取りました", card)
            print("is_valid_playの真偽値は", self.is_valid_play(card))
            if self.is_valid_play(card):
                print("現在の手札は", self.hands[player])
                self.hands[player].remove(card)
                print("カードを出した現在の手札は", self.hands[player])
                self.discard_pile.append(card)
                #print("このプレイヤーの手札は", self.hands[player])
                #print("現在の捨て札の一番上は", self.discard_pile[-1])
                self.apply_card_play(card)      # カードを判定する関数
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
            "next_player": self.players_turn[self.current_turn],
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
 