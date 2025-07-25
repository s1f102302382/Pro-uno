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
            case 'initial_hands':
                console.log("hands is", data.hands);
                tmphand = [...data.hands];
                tmphand = sort_hands(tmphand);
                console.log("after sort hand is", tmphand);
                show_your_hand(tmphand);
                break;
            case 'game-update':
                console.log("現在はgame-updateが呼び起こされた")
                console.log("playerName", playerName);
                show_other_player_hands_number(data.player);
                const NEXT = data.next_player;
                if (NEXT !== playerName) {
                    let NEXT_PLAYER = document.querySelector('.message').textContent = NEXT + " is the next";
                } else {
                    let NEXT_PLAYER = document.querySelector('.message').textContent = "Is your turn";
                }
                let Your_number_of_cards = data.player[playerName];
                console.log("Your_number_of_cards is", Your_number_of_cards);
                if (tmphand.length !== Your_number_of_cards){
                    console.log("ローカルでのカードの枚数は", tmphand.length);
                    console.log("あなたのカードの枚数は", Your_number_of_cards);
                    console.log("最新のカードの枚数と一致しないため最新のカードを取得します...");
                    get_latest_card();
                    return;
                }
                /*
                //自分のターンでなければ若干色が薄くなる
                const isMyTurn = (data.next_player === player);
                document.querySelectorAll('.card').forEach(card => {
                    card.style.opacity = isMyTurn ? 1 : 0.5;
                    card.style.pointerEvents = isMyTurn ? 'all' : 'none';
                });
                */
                const top_card = data.top_card;
                show_top_card(top_card);
                console.log("next player is", data.next_player);
                break;
            case 'latest_hands':
                console.log("現在はlateset_hands")
                tmphand = data.hands;
                tmphand = sort_hands(tmphand);
                console.log("after sort hand is", tmphand);
                console.log("lateset_handsを呼び起こして、現在の手札は", tmphand);
                show_your_hand(tmphand);
                break;
            case 'game-end':
                const message = data.message
                const winner = data.winner;
                if (winner !== playerName){
                    let messageshow = document.querySelector('.message').textContent = message;
                } else {
                    let messageshow = document.querySelector('.message').textContent = "You are winner !";
                }
                break;
            case 'error':
                alert("あなたのターンではありません");
                break;
        }
        /*
        if (data.type === 'game-update'){

            console.log("playerName", playerName);
            let Your_number_of_cards = data.player[playerName];
            console.log("Your_number_of_cards is", Your_number_of_cards);
            if (tmphand.length !== Your_number_of_cards){
                console.log("ローカルでのカードの枚数は", tmphand.length);
                console.log("あなたのカードの枚数は", Your_number_of_cards);
                console.log("最新のカードの枚数と一致しないため最新のカードを取得します...");
                get_latest_card();
                return;
            }
        }
        */

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
    yourdeckarea.innerHTML = '';

    const numberOfcards = cards.length;
    console.log("並べるカードの数は", numberOfcards);
    let ulElement = document.createElement("ul");
    if (ulElement) {
        ulElement.style.setProperty("--length", numberOfcards); // --length を設定
    }
    yourdeckarea.appendChild(ulElement);
    console.log("show_your_hands の hands", cards);

    for (let i = 0; i < numberOfcards; i++) {
        const card = cards[i];
        const li = document.createElement('li');
        const div = document.createElement('div');
        div.className = 'card';
        div.style.setProperty("--index", i);
        const img = document.createElement('img');

        img.src = staticUrl + `${card}.jpg`;      // Django の static URL を使って画像のパスを生成
        img.alt = `${card}のカード`;

        div.appendChild(img);
        div.addEventListener('click', () => play_card(card));
        li.appendChild(div);
        ulElement.appendChild(li);
        //yourdeckarea.appendChild(div);
        //yourdeckarea.appendChild(li);
    }
    /*
    cards.forEach(card => {
        const li = document.createElement('li');
        const div = document.createElement('div');
        div.className = 'card';
        const img = document.createElement('img');

        img.src = staticUrl + `${card}.jpg`;      // Django の static URL を使って画像のパスを生成
        img.alt = `${card}のカード`;

        div.appendChild(img);
        div.addEventListener('click', () => play_card(card));
        li.appendChild(div);
        //yourdeckarea.appendChild(div);
        yourdeckarea.appendChild(li);
    });
    */
};

const show_top_card = (card) => {
    const topcardarea = document.querySelector('.top-card');
    topcardarea.innerHTML = '';
    const img = document.createElement('img');
    if (card === 80 || card === 90) {card = '0' + String(card);}    // もし色が赤の色を変更できるカードならば、最初に0をつける
    img.src = staticUrl + `${card}.jpg`;
    img.alt = `${card}のカード`;

    topcardarea.appendChild(img);
};

const play_card = (card) => {
    console.log("playe_card function is work!");
    if (card === 80 || card === 90) {    // 80, 90 はワイルドカード
        selectedCard = card;    // 選択待ちカードを保存
        document.getElementById("color-picker").style.display = "block";  // 色選択UIを表示
        return;     // すぐには送信せずに待機
    }
    console.log("you played card is", card);
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

    console.log("Sending message in sendCardToserver is", message);
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
        action: 'get_latest_hands',
        player: playerName,
    })

    console.log("Sending message", message);
    UNOSocket.send(message);
}

const sort_hands = (hands) => {
    // red = 0, bule = 1, yellow = 2, green = 3
    const red = 0; const blue = 1; const yellow = 2; const green = 3; const change_color = 80; const draw4 = 90;
    let result = [];        let red_array = [];     let blue_array = [];
    let yellow_array = [];  let green_array = [];   let other = [];

    for (let i = 0; i < hands.length; i++) {
        if (hands[i] < 40) {// 数字カードの場合
            let color = Math.floor(hands[i] / 10);  // 商を整数にする
            switch (color) {
                case red:
                    red_array.push(hands[i]);
                    break;
                case blue:
                    blue_array.push(hands[i]);
                    break;
                case yellow:
                    yellow_array.push(hands[i]);
                    break;
                case green:
                    green_array.push(hands[i]);
                    break;
            }
        } else if (hands[i] % 100>= 40 && hands[i] % 100 < 80) {// 機能カードの場合は百の桁が色
            let color = Math.floor(hands[i] / 100);     // 商を整数にする
            switch (color) {
                case red:
                    red_array.push(hands[i]);
                    break;
                case blue:
                    blue_array.push(hands[i]);
                    break;
                case yellow:
                    yellow_array.push(hands[i]);
                    break;
                case green:
                    green_array.push(hands[i]);
                    break;
                default:
                    break;
            }
        } else {
            // 80か90がの残る
            other.push(hands[i]);
        }
    }
    // 下で全部降順でソート
    red_array.sort((a, b) => b - a);
    blue_array.sort((a, b) => b - a);
    yellow_array.sort((a, b) => b - a);
    green_array.sort((a, b) => b - a);

    // resultに結合する
    result = [...red_array, ...blue_array, ...yellow_array, ...green_array, ...other];
    hands = [];
    hands = [...result];
    return hands;
}

const show_other_player_hands_number = (player) => {
    // data.playerで引数を受け取る
    let i = 0;
    //const area = ["upper", "right", "left"];
    const area = [".handcontainer.upper", ".handcontainer.right", ".handcontainer.left"];

    // 自分の名前のキーを除外する
    const keys = Object.keys(player).filter(key => key !== playerName);
    console.log(keys);
    for (const key of keys) {
        const otherPlayer = document.querySelector(area[i]);
        if (!otherPlayer) {
            console.error(`Error: ${area[i]} が見つかりません`);
            continue;
        }
        otherPlayer.innerHTML = '';
        let h2Element = document.createElement("h2");
        h2Element.textContent = `${key}: ${player[key]}`;
        otherPlayer.appendChild(h2Element);
        i++;
    }
    return;
}

const main = () => {
    //console.log("start main function");
    initWebsocket();

}

window.onload = main;