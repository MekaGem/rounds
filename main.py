import json
import uuid
import random
import ssl

import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.template
import tornado.httpserver

import game.level
import game.message
import game.player
import game.util

DELTA = 1000.0 / 60

level = game.level.Level(10, 5)
connection_to_player = {}


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        loader = tornado.template.Loader('.')
        self.write(loader.load('game.html').generate())


class WSHandler(tornado.websocket.WebSocketHandler):
    connections = set()

    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.id = uuid.uuid4()

    def check_origin(self, origin):
        return True

    def open(self):
        WSHandler.connections.add(self)

        self.write_message(game.message.server_timestamp())
        self.write_message(game.message.level_info(level))

        x = random.randint(0, level.width - 1)
        y = random.randint(0, level.height - 1)
        player = game.player.Player(x, y, 4)
        level.add_player(player)

        connection_to_player[self.id] = player.id
        self.announce_to_all(game.message.player_update(player))

        for player in level.players():
            self.write_message(game.message.player_update(player))

    def on_message(self, message):
        message = json.loads(message)
        # print('received: {}'.format(message))

        player_id = connection_to_player[self.id]
        player = level.get_player(player_id)

        action = message['action']
        if action == 'MOVE':
            player.move(message['direction'])
        elif action == 'STAND':
            player.move(None)

    def on_close(self):
        WSHandler.connections.remove(self)

        player_id = connection_to_player[self.id]
        player = level.get_player(player_id)
        level.remove_player(player_id)
        print('logged out {}'.format(player_id))

        self.announce_to_all(game.message.player_removed(player))

    @staticmethod
    def announce_to_all(message):
        for connection in WSHandler.connections:
            connection.write_message(message)

announced = [0]

def update():
    for player in level.players():
        if player.need_update():
            announced[0] += 1
            print(announced[0])

            WSHandler.announce_to_all(game.message.player_update(player))
            player.updated()

    level.update(DELTA / 1000)


def main():
    application = tornado.web.Application([
        (r'/ws', WSHandler),
        (r'/', MainHandler),
        (r'/(.*)', tornado.web.StaticFileHandler, {'path': './resources'}),
    ])
    # import os
    # print(os.listdir('.'))

    ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_ctx.load_cert_chain('server.crt', 'server.key')
    server = tornado.httpserver.HTTPServer(application, ssl_options=ssl_ctx)
    server.listen(9090)

    game_update = tornado.ioloop.PeriodicCallback(update, DELTA, tornado.ioloop.IOLoop.instance())
    game_update.start()
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()
