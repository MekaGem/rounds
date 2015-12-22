// Map info
var width = 0;
var height = 0;
var map = [];
var dx = 0;
var dy = 0;

// Players info
var units = {};

// Canvas
var stage;
var canvas;
var preload;
var container;
var time;
var queue;
var announce;

// TO DELETE
var doge;

var CELL_SIZE = 32;

//function getTimestamp() {
//    return new Date().getTime()
//}

function createMap() {
    for (var x = 0; x < width; ++x) {
        var row = [];
        for (var y = 0; y < height; ++y) {
            var cell = new createjs.Shape();
            cell.x = x * CELL_SIZE;
            cell.y = y * CELL_SIZE;
            cell.graphics.beginStroke('green').rect(0, -CELL_SIZE, CELL_SIZE, CELL_SIZE);
            row.push(cell);
            container.addChildAt(cell, 0);
        }
        map.push(row);
    }
}

function updateMap() {
    var cx = canvas.width / 2;
    var cy = canvas.height / 2;

    if (container) {
        container.x = cx;
        container.y = cy;
    }

    dx = -(width * CELL_SIZE) / 2;
    dy = (height * CELL_SIZE) / 2;

    for (var x = 0; x < width; ++x) {
        for (var y = 0; y < height; ++y) {
            var cell = map[x][y];
            cell.x = dx + x * CELL_SIZE;
            cell.y = dy - y * CELL_SIZE;
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
    var image = preload.getResult('doge');
    doge = new createjs.Bitmap(image);

    doge.x = -100;
    doge.y = 100;
    doge.scaleX = 50 / image.width;
    doge.scaleY = 50 / image.height;
    doge.regX = 450;
    doge.regY = 450;
}

function init() {
    canvas = document.getElementById('canvas');

    preload = new createjs.LoadQueue();
    preload.on('complete', handleComplete, this);
    preload.loadFile({id: 'doge', src: 'doge.png'});

    stage = new createjs.Stage('canvas');
    window.onresize = onResize;

    container = new createjs.Container();
    stage.addChild(container);

    time = new createjs.Text('', '14px Arial', '#FFFFFF');
    stage.addChild(time);

    queue = new createjs.Text('', '24px Arial', '#FFFFFF');
    queue.visible = false;

    announce = new createjs.Text('', '24px Arial', '#FFFFFF');
    announce.visible = false;

    createjs.Ticker.addEventListener('tick', tick);
    createjs.Ticker.framerate = 30;

    this.document.onkeydown = keyDown;
    this.document.onkeyup = keyUp;

    onResize();
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

    if (playerId != null) {
        var player = units[playerId];
        console.log();
        container.setChildIndex(player, container.numChildren - 1);
    }

    timer += event.delta;
    time.text = Math.floor(timer);

    var h_direction = 0;
    if (keys[LEFT]) h_direction = -1; // 'LEFT';
    if (keys[RIGHT]) h_direction = 1; // 'RIGHT';

    var v_direction = 0;
    if (keys[UP]) v_direction = 1; // 'UP';
    if (keys[DOWN]) v_direction = -1; // 'DOWN';

    if (h_direction != direction[0] || v_direction != direction[1]) {
        direction[0] = h_direction;
        direction[1] = v_direction;

        var message;
        if (direction == null) {
            message = {
                'action': 'STAND'
            };
        } else {
            message ={
                'action': 'MOVE',
                'direction': direction
            };
        }
        sendMessage(message);
    }

    for (var unitId in units) {
        if (units.hasOwnProperty(unitId)) {
            actUnit(units[unitId], event.delta / 1000);
        }
    }

    stage.update();
}

function setNickname() {
    connect();

    container.addChild(queue);
    container.addChild(announce);

    stage.addChild(doge);

    var nick = document.getElementById('nickname').value;

    var nickname = new createjs.Text(nick, '24px Arial', '#FFFFFF');
    nickname.x = 300;
    nickname.y = 30;
    stage.addChild(nickname);

    document.getElementById('nickname_form').style.visibility = 'hidden';
}

function updateQueue(waiting, total) {
    queue.text = 'Waiting for players... WAITING/TOTAL'
        .replace('WAITING', waiting)
        .replace('TOTAL', total);
    queue.x = -queue.getMeasuredWidth() / 2;
    queue.y = -queue.getMeasuredHeight() / 2;
    queue.visible = true;
}

function changeAnnounce(message) {
    announce.text = message;
    announce.x = -announce.getMeasuredWidth() / 2;
    announce.y = -announce.getMeasuredHeight() / 2;
    announce.visible = true;

    createjs.Tween.get(announce)
        .wait(2000)
        .to({visible: false});
}