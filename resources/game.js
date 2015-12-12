// Map info
var width = 0;
var height = 0;
var map = [];

// Players info
var players = {};

// Canvas
var stage;
var canvas;
var preload;
var time;
var doge;

var CELL_SIZE = 32;

// Network
var host = 'ws://HOST:9090/ws'.replace('HOST', document.domain);
var socket;

//function getTimestamp() {
//    return new Date().getTime()
//}

function updatePlayer(player, content, timestamp) {
    player.x = content['x'] * CELL_SIZE;
    player.y = CELL_SIZE * 5 - content['y'] * CELL_SIZE;
    player.xSpeed = 0;
    player.ySpeed = 0;

    var moving = content['moving'];

    if (moving) {
        player.xSpeed = CELL_SIZE * moving['x_speed'];
        player.ySpeed = CELL_SIZE * moving['y_speed'];
    }
}

function actPlayer(circle, delta) {
    circle.x += circle.xSpeed * delta;
    circle.y -= circle.ySpeed * delta;
}

function createMap() {
    for (var x = 0; x < width; ++x) {
        var row = [];
        for (var y = 0; y < height; ++y) {
            var cell = new createjs.Shape();
            cell.x = x * CELL_SIZE;
            cell.y = y * CELL_SIZE;
            cell.graphics.beginStroke("green").rect(0, 0, CELL_SIZE, CELL_SIZE);
            row.push(cell);
            stage.addChild(cell);
        }
        map.push(row);
    }
}

function updateMap() {
    var cx = (canvas.width - (width * CELL_SIZE)) / 2;
    var cy = (canvas.height - (height * CELL_SIZE)) / 2;
    for (var x = 0; x < width; ++x) {
        for (var y = 0; y < height; ++y) {
            var cell = map[x][y];
            cell.x = cx + x * CELL_SIZE;
            cell.y = cy + y * CELL_SIZE;
        }
    }
}

function onResize() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    var nickname_form = document.getElementById('nickname_form');
    var login_width = 240;
    var login_height = 120;
    nickname_form.style.position = 'absolute';
    nickname_form.style.width = login_width + 'px';
    nickname_form.style.height = login_height + 'px';

    nickname_form.style.left = (window.innerWidth - login_width) / 2 + 'px';
    nickname_form.style.top = (window.innerHeight - login_height) / 2 + 'px';

    updateMap();
}

function handleComplete() {
    var image = preload.getResult("doge");
    doge = new createjs.Bitmap(image);

    doge.x = -100;
    doge.y = 100;
    doge.scaleX = 50 / image.width;
    doge.scaleY = 50 / image.height;
    doge.regX = 450;
    doge.regY = 450;
}

function init() {
    canvas = document.getElementById("canvas");

    onResize();

    preload = new createjs.LoadQueue();
    preload.on("complete", handleComplete, this);
    preload.loadFile({id: "doge", src: "doge.png"});

    stage = new createjs.Stage("canvas");
    window.onresize = onResize;

    time = new createjs.Text('', '14px Arial', '#FFFFFF');
    stage.addChild(time);

    createjs.Ticker.addEventListener("tick", tick);
    createjs.Ticker.framerate = 30;

    this.document.onkeydown = keyDown;
    this.document.onkeyup = keyUp;
}

var direction = [0, 0];
var timer = 0;
function tick(event) {
    if (doge) {
        doge.x += 5;
        doge.rotation += 3;

        if (doge.x >= canvas.width + 100) {
            doge.x -= canvas.width + 200;
        }
    }

    timer += event.delta;
    time.text = Math.floor(timer);

    var h_direction = 0;
    if (keys[LEFT]) h_direction = -1; // "LEFT";
    if (keys[RIGHT]) h_direction = 1; // "RIGHT";

    var v_direction = 0;
    if (keys[UP]) v_direction = 1; // "UP";
    if (keys[DOWN]) v_direction = -1; // "DOWN";

    if (h_direction != direction[0] || v_direction != direction[1]) {
        direction[0] = h_direction;
        direction[1] = v_direction;

        var message;
        if (direction == null) {
            message = JSON.stringify({
                "action": "STAND"
            });
        } else {
            message = JSON.stringify({
                "action": "MOVE",
                "direction": direction
            });
        }
        socket.send(message);
    }

    for (var player_id in players) {
        if (players.hasOwnProperty(player_id)) {
            actPlayer(players[player_id], event.delta / 1000);
        }
    }

    stage.update();
}

function setNickname() {
    socket = connect();

    stage.addChild(doge);

    var nick = document.getElementById('nickname').value;

    var nickname = new createjs.Text(nick, '24px Arial', '#FFFFFF');
    nickname.x = 300;
    nickname.y = 30;
    stage.addChild(nickname);

    document.getElementById('nickname_form').style.visibility = "hidden";
}