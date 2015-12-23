function drawPlayer(unit) {
    var color;
    if (unit.alive) {
        color = 'yellow'
    } else {
        color = unit.resurrection > 0 ? 'red' : 'orange'
    }

    var w = unit.w * CELL_SIZE;
    var h = unit.h * CELL_SIZE;

    unit.graphics.clear();
    unit.graphics.beginFill(color).drawRect(-w / 2, -h / 2, w, h).endFill();

    if (playerId == unit.id) {
        unit.graphics.beginStroke('white').setStrokeStyle(2).drawRect(-w / 2, -h / 2, w, h).endStroke();
        unit.graphics.beginFill('black').rect(-3, -3, 6, 6).endFill();
    }

    if (unit.resurrection) {
        unit.graphics.beginStroke('white');
        unit.graphics.setStrokeStyle(3);
        unit.graphics.arc(0, 0, w / 4, 0, unit.resurrection * 2 * Math.PI, false);
        unit.graphics.endStroke();
    }

    if (unit.invulnerable) {
        unit.alpha = 0.5;
    } else {
        unit.alpha = 1;
    }
}

function drawEnemy(unit) {
    var w = unit.w * CELL_SIZE;
    var h = unit.h * CELL_SIZE;

    unit.graphics.clear();
    unit.graphics.beginFill('blue').drawRect(-w / 2, -h / 2, w, h);
}

function drawTurret(unit) {
    var w = unit.w * CELL_SIZE;
    var h = unit.h * CELL_SIZE;

    unit.graphics.clear();
    unit.graphics.beginFill('cyan').drawRect(-w / 2, -h / 2, w, h);

    if (unit.preparation) {
        unit.graphics.endFill();
        unit.graphics.beginStroke('black');
        unit.graphics.setStrokeStyle(3);
        unit.graphics.arc(0, 0, w / 4, 0, unit.preparation * 2 * Math.PI, false);
    } else {
        unit.graphics.beginFill('yellow').drawCircle(0, 0, w / 5);
    }
}

function drawTurretBullet(unit) {
    var w = unit.w * CELL_SIZE;
    var h = unit.h * CELL_SIZE;

    unit.graphics.clear();
    unit.graphics.beginFill('cyan').drawRect(-w / 2, -h / 2, w, h);
}

function drawSpeedBonus(unit) {
    var w = unit.w * CELL_SIZE;
    var h = unit.h * CELL_SIZE;

    unit.graphics.clear();
    unit.graphics.beginFill('gray').drawRect(-w / 2, -h / 2, w, h);
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
        unit.invulnerable = content['invulnerable'];
    }

    if (unit.type == 'TURRET') {
        unit.preparation = content['preparation']['left'];
        unit.preparationSpeed = content['preparation']['speed'];
    }

    var moving = content['moving'];
    unit.xSpeed = CELL_SIZE * moving['x_speed'];
    unit.ySpeed = CELL_SIZE * moving['y_speed'];
}

var drawUnitFunctions = {
    'PLAYER': drawPlayer,
    'ENEMY': drawEnemy,
    'TURRET': drawTurret,
    'TURRET_BULLET': drawTurretBullet,
    'SPEED_BONUS': drawSpeedBonus
};

function drawUnit(unit) {
    drawUnitFunctions[unit.type](unit);
}

function actUnit(unit, delta) {
    unit.x += unit.xSpeed * delta;
    unit.y -= unit.ySpeed * delta;

    if (unit.type == 'PLAYER' && unit.resurrection) {
        unit.resurrection = Math.max(0, unit.resurrection - delta * unit.resurrectionSpeed);
        drawUnit(unit)
    }

    if (unit.type == 'TURRET' && unit.preparation) {
        unit.preparation = Math.max(0, unit.preparation - delta * unit.preparationSpeed);
        drawUnit(unit)
    }
}

