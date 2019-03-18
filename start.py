import logging
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from app.app import app
from app.server_configuration import SERVER_PORT


if __name__ == '__main__':
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(SERVER_PORT)
    logging.debug("Started Server on http://localhost:" + str(SERVER_PORT))
    IOLoop.instance().start()
