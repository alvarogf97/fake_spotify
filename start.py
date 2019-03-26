import logging
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from app.app import app
from app.server_configuration import SERVER_PORT


def migrate_db():
    import os
    from os.path import isfile, isdir
    from app.app import music_path
    from app.models.group import Group, Album, Song
    from app.utils.string_utils import uncrop_withespaces
    for node in os.listdir(music_path):
        group_path = music_path + '/' + node
        if isdir(group_path):
            group_name = uncrop_withespaces(node)
            print('CREATE GROUP: ' + group_name)
            Group.c_make(group_name, group_path)
            for _node in os.listdir(group_path):
                album_path = group_path + '/' + _node
                if isdir(album_path):
                    album_name = uncrop_withespaces(_node)
                    print('CREATE ALBUM: ' + album_name)
                    Album.c_make(album_name, group_name, album_path)
                    for __node in os.listdir(album_path):
                        song_path = music_path + '/' + node + '/' + _node + '/' + __node
                        if isfile(song_path):
                            song_name = uncrop_withespaces(__node)
                            print('CREATE SONG: ' + song_name)
                            Song.c_make(song_name, album_name, group_name, song_path)


if __name__ == '__main__':
    migrate_db()
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(SERVER_PORT)
    logging.debug("Started Server on http://localhost:" + str(SERVER_PORT))
    IOLoop.instance().start()
