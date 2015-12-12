var host = 'ws://HOST:9090/ws'.replace('HOST', document.domain);
var socket;

function onOpen() {
    console.log('Socket connected');
    sendMessage({
        'action': 'SEARCH_GAME'
    });
}

function onMessage(message) {
    message = JSON.parse(message.data);
    var type = message['type'];
    var content = message['content'];
    var timestamp = message['timestamp'];

    var player;
    if (type == 'PLAYER_UPDATE') {
        if (content['id'] in players) {
            player = players[content['id']];
            updatePlayer(player, content, timestamp);
        } else {
            player = new createjs.Shape();
            console.log((content['x'] - content['width'] / 2) * CELL_SIZE);
            player.graphics.beginFill('red').drawRect(
                (-content['width'] / 2) * CELL_SIZE,
                (-content['height'] / 2) * CELL_SIZE,
                content['width'] * CELL_SIZE,
                content['height'] * CELL_SIZE
            );
            updatePlayer(player, content, timestamp);

            players[content['id']] = player;
            container.addChild(player);
        }
    } else if (type == 'PLAYER_REMOVED') {
        if (content['id'] in players) {
            player = players[content['id']];
            container.removeChild(player);
            delete players[content['id']];
        }
    } else if (type == 'SERVER_TIMESTAMP') {
        // server_timestamp_diff = getTimestamp() - timestamp;
        // console.log(server_timestamp_diff)
    } else if (type == 'ROOM_INFO') {
        width = content['width'];
        height = content['height'];
        console.log('width = ' + width);
        createMap();
        updateMap();
    }
}

function onClose() {
    console.log('Socket disconnected');
}

function connect() {
    socket = new WebSocket(host);
    console.log(socket);

    if (socket) {
        socket.onopen = onOpen;
        socket.onmessage = onMessage;
        socket.onclose = onClose;
    } else {
        console.log('Invalid socket');
    }
}

function sendMessage(message) {
    socket.send(JSON.stringify(message));
}