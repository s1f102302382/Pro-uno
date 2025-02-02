const roomName = JSON.parse(document.getElementById('room-name').textContent);

const Websocket = function() {
    Socket = new Websocket(
        'ws://'
        + window.location.host
        + '/ws/uno/'
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
    Websocket.onmessage = (event) {
        const data = JSON.parse(event.data);

        console.log("Listener is work");

        switch(data) {
            case '':
                // pass
                break;
            
        }
    }
}