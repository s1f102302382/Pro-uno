let UNOSocket;
let tmphand;
let selectedCard = null;
const roomName = JSON.parse(document.getElementById('room-name').textContent);
const playerName = JSON.parse(document.getElementById('player-name').textContent);
//console.log(playerName);

const initWebsocket = function() {
    UNOSocket = new WebSocket(
        'ws://'
        + window.location.host
        + '/ws/uno/room_index/'
        + roomName
        + '/'
    );
    //console.log("creat s webSocket");

    UNOSocket.onopen = () => {
        console.log("websocket connect");
        Listener(UNOSocket);
        // ちゃんと接続後に'send_join'を実行
        sent_join(playerName);
    };

    UNOSocket.onerror = function(error) {
        console.log("websocket error", error);
    };
    
    UNOSocket.onclose = function() {
        console.log("websocket is closed!");
    };

};

const Listener = (Websocket) => {
    // サーバーからデータを受信
    Websocket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log("get data form server is\n", data);
        switch(data.type) {
            case 'game-update':

                if (tmphand && (tmphand.length !== data.player[playerName])){
                    get_latest_card();
                }
                const isMyTurn = (data.next_player === playerName);
                document.querySelectorAll('.card').forEach(card => {
                    card.style.opacity = isMyTurn ? 1 : 0.5;
                    card.style.pointerEvents = isMyTurn ? 'all' : 'none';
                });
                
                const yourhand = data.player[playerName]?.hand;

                if (!yourhand) {    // もし自分宛じゃなければ、保存した手札を使う;
                    //console.log("if yourhand === nullを実行中 --------------------ifを実行");
                    //console.log("tmphand is", tmphand);
                    show_your_hand(tmphand);
                } else {                    // 
                    //console.log("---------------------elseを実行");
                    show_your_hand(yourhand);
                    //console.log("before change tmphand is", tmphand);
                    tmphand = [...yourhand];
                    //console.log("after change tmpcard is ", tmphand);
                }
                const top_card = data.top_card;
                show_top_card(top_card);

                break;
            case 'latest_hands':
                tmphand = data.hands;
                show_top_card(tmphand);
                break;
            case 'error':
                alert("あなたのターンではありません");
                break;
        }
    }
};

const sent_join = (PLAYERNAME) => {
    UNOSocket.send(JSON.stringify({
        action: 'join',
        player: PLAYERNAME
    }));
};

const show_your_hand = (cards) => {
    const yourdeckarea = document.querySelector('.your');
    /*
    const existingCards = yourdeckarea.querySelectorAll('.card img');

    if (existingCards.length === cards.length 
        &&
        [...existingCards].every((img.alt) === `${cards[i]}のカード`)) {
            return;// 変更がなければ更新しない
        }
    */
    yourdeckarea.innerHTML = '';

    cards.forEach(card => {
        const div = document.createElement('div');
        div.className = 'card';
        const img = document.createElement('img');

        //img.src = `{% static 'uno/img/${card}.jpg' %}`;
        img.src = staticUrl + `${card}.jpg`;      // Django の static URL を使って画像のパスを生成
        img.alt = `${card}のカード`;

        div.appendChild(img);
        div.addEventListener('click', () => play_card(card));
        yourdeckarea.appendChild(div);
    });
};

const show_top_card = (card) => {
    const topcardarea = document.querySelector('.top-card');
    topcardarea.innerHTML = '';
    const img = document.createElement('img');
    img.src = staticUrl + `${card}.jpg`;
    img.alt = `${card}のカード`;

    topcardarea.appendChild(img);
};

const play_card = (card) => {
    console.log("playe_card function is work!");
    if (card === 80 || card === 90) {    // 80, 90 はワイルドカード
        // ここで画面に色を選択するようにな感じのものが出てくる
        // red = 0, bule = 1, yellow = 2, green = 3
        // color = 選択した色 * 100;
        // card += color:
        selectedCard = card;    // 選択待ちカードを保存
        document.getElementById("color-picker").style.display = "block";  // 色選択UIを表示
        return;     // すぐには送信せずに待機
    }
    console.log("you played card is", card);
    /*
    UNOSocket.send(JSON.stringify({
        action: 'play_card',
        card: card,
        player: playerName,
    }));
    */
   sendCardToServer(card);
};

const selectColor = (color) => {
    if (selectedCard !== null) {
        selectedCard += color * 100;    // 選択した色を加算
        sendCardToServer(selectedCard);
        selectedCard = null;    // クリア
        document.getElementById("color-picker").style.display = "none";     // UIを非表示
    }
};

// サーバーにカードを送信する関数
const sendCardToServer = (card) => {
    console.log("sendCardToServer function is called!");
    console.log("you played card is", card);

    // もし接続ができてない場合
    if (!UNOSocket || UNOSocket.readyState !== WebSocket.OPEN) {
        console.error("WebSocket is not open. Cannot send message.");
        return;
    }

    const message = JSON.stringify({
        action: 'play_card',
        card: card,
        player: playerName,
    });
    /*
        UNOSocket.send(JSON.stringify({
        action: 'play_card',
        card: card,
        player: playerName,
    }));
    */

    console.log("Sending message", message);
    UNOSocket.send(message);
};

const draw_card = () => {
    console.log("draw_card function is work!");
    UNOSocket.send(JSON.stringify({
        action: 'draw',
        player: playerName
    }));
}

const get_latest_card = () => {
    const message = JSON.stringify({
        action: 'play_card',
        player: playerName,
    })

    console.log("Sending message", message);
    UNOSocket.send(message);
}

const main = () => {
    //console.log("start main function");
    initWebsocket();

}

window.onload = main;