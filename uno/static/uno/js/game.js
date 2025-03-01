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
        //console.log("your hand is:", yourhand);
        //console.log("Listener is work");
    }
}

const sent_join = (PLAYERNAME) => {
    UNOSocket.send(JSON.stringify({
        action: 'join',
        player: PLAYERNAME
    }));
}

const show_your_hand = (array) => {
    const yourdeckarea = document.querySelector('.your');
    yourdeckarea.innerHTML = '';

    for (let i=0; i < array.length; i++) {
        
    }
}

const main = () => {
    console.log("start main function");
    initWebsocket();


}

window.onload = main;