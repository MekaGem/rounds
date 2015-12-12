var LEFT = 37;
var UP = 38;
var RIGHT = 39;
var DOWN = 40;

var keys = {};

function keyDown(event) {
    keys[event.keyCode] = true;
}

function keyUp(event) {
    keys[event.keyCode] = false;
}