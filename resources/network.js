var host = 'ws://HOST:9090/ws'.replace('HOST', document.domain);
var socket;
var playerId;

function onOpen() {
    console.log('Socket connected');
    sendMessage({
        'action': 'SEARCH_GAME'
    });
}

function onUnitUpdate(content, timestamp) {
    var unit;
    if (content['id'] in units) {
        unit = units[content['id']];
        updateUnit(unit, content);
        drawUnit(unit);
    } else {
        console.log('Created ' + content['type']);
        unit = new createjs.Shape();
        updateUnit(unit, content);
        drawUnit(unit);
        units[content['id']] = unit;
        container.addChild(unit);
    }
}

function onUnitRemoved(content, timestamp) {
    if (content['id'] in units) {
        var unit = units[content['id']];
        container.removeChild(unit);
        delete units[content['id']];
    }
}

function onRoomInfo(content, timestamp) {
    width = content['width'];
    height = content['height'];
    createMap();
    updateMap();
    queue.visible = false;
}

function onInQueue(content, timestamp) {
    updateQueue(content['waiting'], content['total']);
}

function onRoundStarted(content, timestamp) {
    changeAnnounce('Round started!');
}

function onPlayerId(content, timestamp) {
    playerId = content['id'];
}

var onMessageFunctions = {
    'UNIT_UPDATE': onUnitUpdate,
    'UNIT_REMOVED': onUnitRemoved,
    'ROOM_INFO': onRoomInfo,
    'IN_QUEUE': onInQueue,
    'ROUND_STARTED': onRoundStarted,
    'PLAYER_ID': onPlayerId
};

function onMessage(message) {
    message = JSON.parse(message.data);
    var type = message['type'];
    var content = message['content'];
    var timestamp = message['timestamp'];
    if (type in onMessageFunctions) {
        onMessageFunctions[type](content, timestamp);
    } else {
        console.log('Unhandled message type ' + type);
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