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

    var unit;
    if (type == 'PLAYER_UPDATE' || type == 'ENEMY_UPDATE') {
        if (content['id'] in units) {
            unit = units[content['id']];
            updateUnit(unit, content, timestamp);
        } else {
            unit = new createjs.Shape();
            console.log((content['x'] - content['width'] / 2) * CELL_SIZE);
            unit.graphics.beginFill('red').drawRect(
                (-content['width'] / 2) * CELL_SIZE,
                (-content['height'] / 2) * CELL_SIZE,
                content['width'] * CELL_SIZE,
                content['height'] * CELL_SIZE
            );
            updateUnit(unit, content, timestamp);

            units[content['id']] = unit;
            container.addChild(unit);
        }
    } else if (type == 'PLAYER_REMOVED' || type == 'ENEMY_REMOVED') {
        if (content['id'] in units) {
            unit = units[content['id']];
            container.removeChild(unit);
            delete units[content['id']];
        }
    } else if (type == 'SERVER_TIMESTAMP') {
        // server_timestamp_diff = getTimestamp() - timestamp;
        // console.log(server_timestamp_diff)
    } else if (type == 'ROOM_INFO') {
        width = content['width'];
        height = content['height'];
        createMap();
        updateMap();
        queue.visible = false;
    } else if (type == 'IN_QUEUE') {
        updateQueue(content['waiting'], content['total']);
    } else if (type == 'ROUND_STARTED') {
        changeAnnounce('Round started!');
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