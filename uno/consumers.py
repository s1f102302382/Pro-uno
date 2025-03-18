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
    players_turn = []  # ターンを管理するために
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
        if card is None:
            print("エラー：出されたカードはNoneです")
            return False
        print("is_valid_play に飛びました")
        print("card in is_valid_play is", card)
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
            is_card_change_color = (card % 100 in self.COLOR_CHANGE)
            return (is_same_color or is_card_change_color) == True
        elif (card < 40 and top_card >= 40):
            # 前のカードは特別カードで自分のカードは数字カードの場合
            # -> 同じ色
            is_same_color = (card // 10 == top_card // 100)
            return (is_same_color) == True
        # elif (card >= 40 and top_card >= 40):
        else:
            # 前のカードも今出したカードも特別カードである場合
            # -> 同じ特別カードかまたは色を変えれるカードか
            is_same_function_card = (card % 100 == top_card % 100)
            is_card_change_color = (card % 100 in self.COLOR_CHANGE)
            is_same_color = (card // 100 == top_card //100)
            return (is_same_function_card or is_card_change_color or is_same_color) == True

    def draw_n(self, player ,n):
        UNOConsumer.hands[player] += (UNOConsumer.deck[:n])
        del UNOConsumer.deck[:n]                          # 引いたカードを山札から削除する

    def apply_card_play(self, card):
        print("apply_card_playに入りました")
        print("このカードを受け取りました", card)
        tmpcard = card % 100

        # 特殊カードのマッピングを統合
        special_card = {**UNOConsumer.FUNCTION_CARD, **UNOConsumer.COLOR_CHANGE}

        # 特殊カードでない場合は早期リターン
        if tmpcard not in special_card:
            print("--------------------------------------------effect is none")
            return self.next_turn("none")

        effect = special_card[tmpcard]
        print("--------------------------------------------effect is", effect)

        if effect == "draw2":
            self.next_turn(effect)
            UNOConsumer.draw += 2
            next_player = UNOConsumer.players_turn[UNOConsumer.current_turn]
            can_counter = self.check_next_player_have_draw2_or_draw4(next_player, 'two' if effect == "draw2" else 'four')
            if not can_counter:
                self.draw_n(next_player, UNOConsumer.draw)
                UNOConsumer.draw = 0  # 初期化
                return self.next_turn("none")   # カードを引かせて次のターンいく
        elif effect == "draw4":
            self.next_turn(effect)
            UNOConsumer.draw += 4
            next_player = UNOConsumer.players_turn[UNOConsumer.current_turn]
            can_counter = self.check_next_player_have_draw2_or_draw4(next_player, 'two' if effect == "draw2" else 'four')
            if not can_counter:
                self.draw_n(next_player, UNOConsumer.draw)
                UNOConsumer.draw = 0  # 初期化
                return self.next_turn("none")   # カードを引かせて次のターンいく
        else:
            return self.next_turn(effect)
        return
 
    
    def next_turn(self, effect):
        print("next_turn関数に飛びました!")
        if (effect == "skip"):
            print("skipカードが出されました")
            UNOConsumer.current_turn = (UNOConsumer.current_turn + UNOConsumer.direction * 2) % len(UNOConsumer.players)
        elif (effect == "reverse"):
            print("reverseカードが出されました")
            if len(UNOConsumer.players_turn) == 2:      # もし参加人数が2二人の場合はskipカードと同じ効果である
                print("参加人数が二人のためreverseカードはskipカードと同じ効果を持つ")
                UNOConsumer.current_turn = (UNOConsumer.current_turn + UNOConsumer.direction * 2) % len(UNOConsumer.players)
            else:
                UNOConsumer.direction *= -1
                UNOConsumer.current_turn = (UNOConsumer.current_turn + UNOConsumer.direction) % len(UNOConsumer.players)
        elif (effect == "draw2"):
            #print("draw2カードが出されました\nまだdraw関数が完成されていませんので実装を楽しみに待ってください")
            print("draw2カードが出されました")
            UNOConsumer.current_turn = (UNOConsumer.current_turn + UNOConsumer.direction) % len(UNOConsumer.players)
        elif (effect == "play_all_same_color"):
            print("play_all_same_colorカードが出されました")
            # ここで全て同じ色のカードを出す
            UNOConsumer.current_turn = (UNOConsumer.current_turn + UNOConsumer.direction) % len(UNOConsumer.players)
        elif (effect == "change_color"):
            print("change_colorカードが出されました")
            UNOConsumer.current_turn = (UNOConsumer.current_turn + UNOConsumer.direction) % len(UNOConsumer.players)
        elif (effect == "draw4"):
            print("draw4カードが出されました")
            #self.draw_n(self, 4)
            UNOConsumer.current_turn = (UNOConsumer.current_turn + UNOConsumer.direction) % len(UNOConsumer.players)
        else:
            # 何もなければ数字カードです
            print("数字カードのため通常進行します")
            UNOConsumer.current_turn = (UNOConsumer.current_turn + UNOConsumer.direction) % len(UNOConsumer.players)
        #return self.players_turn[self.current_turn]

    def check_next_player_have_draw2_or_draw4(self, player, two_or_four):
        #self.hands[player]
        tmp = [card % 100 for card in self.hands[player]]
        
        if (two_or_four == 'two'):  # 前の人がdraw2を出したから、draw2またはdraw4がないといけない
            if (60 or 90) in tmp:
                return True
            return False
        else:                       # 前の人がdraw4を出したから、draw4がないといけない
            if (90) in tmp:
                return True
            return False

    def remove_card(self, player, card):
        play_all_same_color = 70
        if card < 40:
            color = card // 10
        elif (40 <= card % 100) and (card % 100 < 80):
            color = card // 100

        if (card % 100) == play_all_same_color:
            # 同じ色のカードだけを残す新しいリストを作成
            self.hands[player] = [i for i in self.hands[player] if not (
                (i < 40 and i // 10 == color) or
                (40 <= (i % 100) <= 70 and i // 100 == color)
            )]
        else:
            if card in self.hands[player]:
                self.hands[player].remove(card)

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
        if action == "join":
            if player not in self.players:
                self.hands[player] = self.create_initial_deck(self.number_of_initial_deck)
                self.players[player] = {"hand": self.hands[player]}
                self.players_turn.append(player)

                response = {
                    "type": "initial_hands",
                    "hands": self.hands[player],
                }
                print("初期の手札は", response)
                self.send(text_data=json.dumps(response))
        elif action == "play_card":
            aviable_player = UNOConsumer.players_turn[UNOConsumer.current_turn]
            print("aviable_player is", aviable_player)
            print("the player who played card is", player)
            if player != aviable_player:
                response = {
                    "type": "error",
                    "message": "現在はあなたのターンではありません"
                }
                print(f"{player} が順番に出さなかった")
                self.send(text_data=json.dumps(response))
            else:
                card = data.get("card")
                falg = False    # カードを出せるかどうかを判断するフラグ
                if ((card % 100) in self.COLOR_CHANGE):
                    card_to_remove = card % 100
                else:
                    card_to_remove = card
                
                print("self.is_valid_play(card) is", self.is_valid_play(card))
                print("card_to_remove in self.hands[player]", card_to_remove in self.hands[player])
                if (self.is_valid_play(card) and card_to_remove in self.hands[player]):
                    #self.hands[player].remove(card_to_remove)
                    self.remove_card(player, card_to_remove)
                    self.discard_pile.append(card)
                    self.apply_card_play(card)
                    response = {
                        "type": "latest_hands",
                        "hands": self.hands[player],
                    }
                    print("カードを出して、最新の手札を送信", response)
                    self.send(text_data=json.dumps(response))

        elif action == "draw":
            aviable_player = UNOConsumer.players_turn[UNOConsumer.current_turn]
            if (player != aviable_player):
                response = {
                    "type": "error",
                    "message": "現在はあなたのターンではありません"
                }
                print(f"{player} が順番に出さなかった")
                self.send(text_data=json.dumps(response))
            else:
                UNOConsumer.draw = 1
                self.draw_n(player, UNOConsumer.draw)
                UNOConsumer.draw = 0

                the_card_you_get = self.hands[player][-1]
                if not self.is_valid_play(the_card_you_get):
                    print(f"{player} がカードを引いたが、出せるカードがなかったのでターンを終了")
                    self.next_turn("none")
        elif action == "get_latest_hands":
            response = {
                "type": "latest_hands",
                "hands": self.hands[player],
            }
            self.send(text_data=json.dumps(response))
        
        print("self.player:", self.players)             # プレイヤーの管理
        print("self.players_turn", self.players_turn)   # プレイヤーごとの手札管理
        print("self.hands:", self.hands)                # ターンを管理するためのリスト
        print("self.deck:", self.deck)                 # 山札
        print("self.discard_pile", self.discard_pile)   # 捨て札山
        print("self.current_turn:", self.current_turn)  # 現在のターン
        print("self.direction:", self.direction)        # 進行方向  時計回りだと１，反時計回りだと-1
        print("self.draw:", self.draw)                 # 引くカードの数の管理

        self.send_game_update()

    def send_game_update(self):
    #def send_game_update(self, cuurent_player=None):
        masked_player = {}
        for player_name in self.players:
            masked_player[player_name] = len(self.hands[player_name])

        update = {
            "type": "game-update",
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
 