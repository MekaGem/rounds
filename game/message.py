import time


def get_timestamp():
    return int(time.time() * 1000)


def player_update(player):
    return _message('PLAYER_UPDATE', player.to_dict())


def player_removed(player):
    return _message('PLAYER_REMOVED', {
        'id': player.id
    })


def enemy_update(enemy):
    return _message('ENEMY_UPDATE', enemy.to_dict())


def enemy_removed(enemy):
    return _message('ENEMY_REMOVED', {
        'id': enemy.id
    })


def room_info(room):
    return _message('ROOM_INFO', {
        'width': room.width,
        'height': room.height
    })


def round_started():
    return _message('ROUND_STARTED', {})


def server_timestamp():
    return _message('SERVER_TIMESTAMP', {})


def in_queue(waiting, total):
    return _message('IN_QUEUE', {
        'waiting': waiting,
        'total': total
    })


def _message(message_type, content):
    return {
        'type': message_type,
        'content': content,
        'timestamp': get_timestamp()
    }
