let UNOSocket;
//console.log("game.js is working!");

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
    console.log("creat s webSocket");

    UNOSocket.onopen = () => {
        console.log("websocket connect");
        Listener(UNOSocket);
        // ちゃんと接続後に'send_join'を実行
        sent_join(playerName);
    }

    UNOSocket.onerror = function(error) {
        console.log("websocket error", error);
    };
    
    UNOSocket.onclose = function() {
        console.log("websocket is closed!");
    }

}

const Listener = (Websocket) => {
    // サーバーからデータを受信
    Websocket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        //console.log("get data form server is\n", data);
        const yourhand = data.player[playerName].hand;
        const top_card = data.top_card;
        console.log(top_card);
        //let yourhand1 = yourhand[0]
        console.log("your hand is:", yourhand);
        //console.log("Listener is work");
        //console.log("show_your_handが実行される前")
        show_your_hand(yourhand);
        //console.log("show_your_handが実行されました。")
}
}

const sent_join = (PLAYERNAME) => {
    UNOSocket.send(JSON.stringify({
        action: 'join',
        player: PLAYERNAME
    }));
}

const show_your_hand = (cards) => {
    const yourdeckarea = document.querySelector('.your');
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
}

const show_top_card = (card) => {
    const topcardarea = document.querySelector('.top-card');
    const img = document.createElement('img');
    img.src = staticUrl + `${card}.jpg`;
    img.alt = `${card}のカード`;

    topcardarea.innerHTML.appendChild(img);
}

const play_card = (card) => {
    console.log("playe_card function is work!");
    console.log("you played card is", card);
    UNOSocket.send(JSON.stringify({
        action: 'play_card',
        card: card,
        player: playerName,
    }));
}

const main = () => {
    console.log("start main function");
    initWebsocket();


}

window.onload = main;