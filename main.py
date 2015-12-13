import json
import uuid
import random
import ssl

import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.template
import tornado.httpserver
import pymongo

import game.room
import game.message
import game.player
import game.util

DELTA = 1000.0 / 60

rooms = []
waiting_for_game = []

connection_to_room = {}
connection_to_player = {}


class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        login = self.get_secure_cookie('login')
        password = self.get_secure_cookie('password')

        if login and password:
            login = login.decode('utf-8')
            password = password.decode('utf-8')

            users = self.application.database['users']
            user = users.find_one({
                'login': login,
                'password': password
            })
            return login if user else None


class GameHandler(BaseHandler):
    # @tornado.web.authenticated
    def get(self):
        self.render('templates/game.html')


class WelcomeHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.write('Welcome, {}!'.format(self.get_cookie('name', default='USER_NAME')))


class LoginHandler(BaseHandler):
    def get(self):
        self.render('templates/login.html')

    def post(self):
        login = self.get_argument('login')
        password = self.get_argument('password')

        users = self.application.database['users']
        user = users.find_one({
            'login': login,
            'password': password
        })

        if user:
            self.set_secure_cookie('login', login)
            self.set_secure_cookie('password', password)
            self.set_cookie('name', login)
            self.redirect('/welcome')
        else:
            self.redirect('/login')


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

    def on_message(self, message):
        message = json.loads(message)

        action = message['action']

        if self not in waiting_for_game:
            if action == 'SEARCH_GAME':
                waiting_for_game.append(self)

            if self.id in connection_to_room:
                room = connection_to_room[self.id]
                player_id = connection_to_player[self.id]
                player = room.get_player(player_id)

                if action == 'MOVE':
                    player.move(message['direction'])
                elif action == 'STAND':
                    player.move(None)

    def on_close(self):
        WSHandler.connections.remove(self)

        if self.id in connection_to_room:
            room = connection_to_room[self.id]
            player_id = connection_to_player[self.id]
            player = room.get_player(player_id)
            room.remove_player(player_id)
            print('logged out {}'.format(player_id))

            del connection_to_room[self.id]
            del connection_to_player[self.id]

            self.announce_to_all(game.message.player_removed(player))

            if not room.players():
                rooms.remove(room)

        if self in waiting_for_game:
            waiting_for_game.remove(self)

    @staticmethod
    def announce_to_all(message):
        for connection in WSHandler.connections:
            connection.write_message(message)

    @staticmethod
    def announce_to_room(room, message):
        for connection in WSHandler.connections:
            if connection.id in connection_to_room and connection_to_room[connection.id] is room:
                connection.write_message(message)

PLAYERS_IN_ROOM = 2
announced = [0, 0]


def update():
    if len(waiting_for_game) != announced[1]:
        for connection in waiting_for_game:
            connection.write_message(game.message.in_queue(len(waiting_for_game), PLAYERS_IN_ROOM))
        announced[1] = len(waiting_for_game)

    if len(waiting_for_game) >= PLAYERS_IN_ROOM:
        connections = []
        for index in range(PLAYERS_IN_ROOM):
            connections.append(waiting_for_game.pop(0))

        room = game.room.Room(15, 15, WSHandler)
        rooms.append(room)

        for connection in connections:
            connection.write_message(game.message.room_info(room))

            x = random.random() * (room.width - 1) + 0.5
            y = random.random() * (room.height - 1) + 0.5
            player = game.player.Player(x, y, 1, 1, 4)
            room.add_player(player)

            connection_to_room[connection.id] = room
            connection_to_player[connection.id] = player.id
            connection.announce_to_room(room, game.message.player_update(player))

            for player in room.players():
                connection.write_message(game.message.player_update(player))

    for room in rooms:
        for player in room.players():
            if player.need_update():
                announced[0] += 1
                print(announced[0])

                WSHandler.announce_to_room(room, game.message.player_update(player))
                player.updated()

        room.update(DELTA / 1000)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/ws', WSHandler),
            (r'/', GameHandler),
            (r'/login', LoginHandler),
            (r'/welcome', WelcomeHandler),
            (r'/(.*)', tornado.web.StaticFileHandler, {'path': './resources'}),
        ]

        settings = {
            'cookie_secret': 'RANDOM_COOKIE_SECRET',
            'login_url': '/login'
        }

        tornado.web.Application.__init__(self, handlers, **settings)

        self.client = pymongo.MongoClient('localhost', 27017)
        self.database = self.client['local']


def main():
    application = Application()

    # ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    # ssl_ctx.load_cert_chain('server.crt', 'server.key')
    ssl_ctx = None
    server = tornado.httpserver.HTTPServer(application, ssl_options=ssl_ctx)
    server.listen(9090)

    game_update = tornado.ioloop.PeriodicCallback(update, DELTA, tornado.ioloop.IOLoop.instance())
    game_update.start()
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()
