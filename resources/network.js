function connect() {
    var socket = new WebSocket(host);

    if (socket) {
        socket.onopen = function () {
            console.log('Socket connected');

            socket.send(JSON.stringify({
                'action': 'SEARCH_GAME'
            }));
        };

        socket.onmessage = function (msg) {
            msg = JSON.parse(msg.data);

            var type = msg['type'];
            var content = msg['content'];
            var timestamp = msg['timestamp'];

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
                    stage.addChild(player);
                }
            } else if (type == 'PLAYER_REMOVED') {
                if (content['id'] in players) {
                    player = players[content['id']];
                    stage.removeChild(player);
                    delete players[content['id']];
                }
            } else if (type == 'SERVER_TIMESTAMP') {
                // server_timestamp_diff = getTimestamp() - timestamp;
                // console.log(server_timestamp_diff)
            } else if (type == 'LEVEL_INFO') {
                //width = content['width'];
                //height = content['height'];
                //createMap();
                //updateMap()
            }
        };

        socket.onclose = function () {
            console.log('Socket disconnected');
        };

        return socket
    } else {
        console.log('Invalid socket');
    }
}