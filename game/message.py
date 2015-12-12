import time


def get_timestamp():
    return int(time.time() * 1000)


def player_update(player):
    return {
        'type': 'PLAYER_UPDATE',
        'content': player.to_dict(),
        'timestamp': get_timestamp()
    }


def player_removed(player):
    return {
        'type': 'PLAYER_REMOVED',
        'content': {
            'id': player.id
        }
    }


def room_info(room):
    print('sending room info')
    return {
        'type': 'ROOM_INFO',
        'content': {
            'width': room.width,
            'height': room.height
        }
    }


def server_timestamp():
    return {
        'type': 'SERVER_TIMESTAMP',
        'timestamp': get_timestamp()
    }
