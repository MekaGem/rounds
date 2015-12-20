import time


def get_timestamp():
    return int(time.time() * 1000)


def unit_update(unit):
    return _message('UNIT_UPDATE', unit.to_dict())


def unit_removed(unit):
    return _message('UNIT_REMOVED', {
        'id': unit.id
    })


def room_info(room):
    return _message('ROOM_INFO', {
        'width': room.width,
        'height': room.height
    })


def player_id(player):
    return _message('PLAYER_ID', {
        'id': player.id
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
