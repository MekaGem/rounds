function drawUnit(unit) {
    var color;
    if (unit.type == 'PLAYER') {
        if (unit.alive) {
            color = 'yellow'
        } else {
            color = unit.resurrection > 0 ? 'red' : 'orange'
        }
    } else {
        color = 'blue'
    }

    var w = unit.w * CELL_SIZE;
    var h = unit.h * CELL_SIZE;

    unit.graphics.clear();
    unit.graphics.beginFill(color).drawRect(-w / 2, -h / 2, w, h);

    if (playerId == unit.id) {
        unit.graphics.beginFill('black').rect(-3, -3, 6, 6);
    }

    if (unit.type == 'PLAYER' && unit.resurrection) {
        unit.graphics.beginStroke('white');
        unit.graphics.setStrokeStyle(3);
        unit.graphics.arc(0, 0, w / 4, 0, unit.resurrection * 2 * Math.PI, false);
    }
}

function updateUnit(unit, content) {
    unit.id = content['id'];
    unit.x = dx + content['x'] * CELL_SIZE;
    unit.y = dy + -content['y'] * CELL_SIZE;
    unit.w = content['width'];
    unit.h = content['height'];
    unit.type = content['type'];

    if (unit.type == 'PLAYER') {
        unit.resurrection = content['resurrection']['left'];
        unit.resurrectionSpeed = content['resurrection']['speed'];
        unit.alive = content['alive'];
    }

    var moving = content['moving'];
    unit.xSpeed = CELL_SIZE * moving['x_speed'];
    unit.ySpeed = CELL_SIZE * moving['y_speed'];
}

function actUnit(unit, delta) {
    unit.x += unit.xSpeed * delta;
    unit.y -= unit.ySpeed * delta;

    if (unit.type == 'PLAYER' && unit.resurrection) {
        unit.resurrection = Math.max(0, unit.resurrection - delta * unit.resurrectionSpeed);
        drawUnit(unit)
    }
}

