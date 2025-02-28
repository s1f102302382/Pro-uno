let Socket;
console.log("game.js is working!");

function is_work(x) {
    return x + 'is work!'
}

const roomName = JSON.parse(document.getElementById('room-name').textContent);

const initWebsocket = function() {
    Socket = new WebSocket(
        'ws://'
        + window.location.host
        + '/ws/uno/room_index/'
        + roomName
        + '/'
    );
    console.log("creat s webSocket");

    Socket.onopen = () => {
        console.log("websocket connect");
        Listener(Socket);
    }
}

const Listener = (Websocket) => {
    Websocket.onmessage = (event) => {
        const data = JSON.parse(event.data);

        console.log("Listener is work");
    }
}

const main = () => {
    console.log("start main function");
    initWebsocket();
    Listener(Socket);

    
}

window.onload = main;