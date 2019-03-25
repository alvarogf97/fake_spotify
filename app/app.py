import logging
import mimetypes
import os
import re
import redis
from flask import Flask, session, request, jsonify, Response, stream_with_context, send_file
from flask_session import Session
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_mongoalchemy import MongoAlchemy
from app.decorators import login_required
from app.server_configuration import DATABASE_NAME, DATABASE_DOMAIN, DATABASE_PORT
# from app.server_configuration import DATABASE_USER, DATABASE_PASSWORD
from app.server_configuration import SESSION_TYPE
from app.session import RedisSessionInterface

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}}, headers=['Content-Type', 'Set-Cookie'], supports_credentials=True)

app.secret_key = '9W[C|i8M9iJALx8UO1nU'
app.config['SESSION_TYPE'] = SESSION_TYPE
app.config['PERMANENT_SESSION_LIFETIME'] = 60
app.config['SESSION_REDIS'] = redis.from_url('redis://localhost:6379')
Session(app)
app.session_interface = RedisSessionInterface()

app.config['MONGOALCHEMY_DATABASE'] = DATABASE_NAME
app.config['MONGOALCHEMY_SERVER'] = DATABASE_DOMAIN
app.config['MONGOALCHEMY_PORT'] = DATABASE_PORT
# app.config['MONGOALCHEMY_USER'] = DATABASE_USER
# app.config['MONGOALCHEMY_PASSWORD'] = DATABASE_PASSWORD
db = MongoAlchemy(app)
bcrypt = Bcrypt(app)
music_path = os.path.dirname(os.path.abspath(__file__)) + '/../music'


########################################################
#                      USERS ROUTES                    #
########################################################
@app.route('/login', methods=['POST'])
def login():
    from app.models.user import User

    session.pop('current_user', None)
    if request.get_json() is None:
        name = request.form.get('name')
        password = request.form.get('password')
    else:
        name = request.get_json().get('name')
        password = request.get_json().get('password')
    if name is None or password is None:
        result = jsonify(status=False, error="NOT ENOUGH ARGUMENTS")
    else:
        user = User.get(name, password)
        if user is None:
            result = jsonify(status=False, error="WRONG USERNAME/PASSWORD")
        else:
            session['current_user'] = user.name
            result = jsonify(status=True, name=user.name)
    return result


@app.route('/logout')
def logout():
    session.pop('current_user', None)
    return jsonify(status=True)


@app.route('/register', methods=['POST'])
def register():
    from app.models.user import User

    name = request.form.get('name')
    password = request.form.get('password')
    if name is None or password is None:
        result = jsonify(status=False, error="NOT ENOUGH ARGUMENTS")
    else:
        new_user = User.make(name, password)
        if new_user is None:
            result = jsonify(status=False, error="USERNAME ALREADY EXISTS")
        else:
            result = jsonify(status=True)
    return result


########################################################
#                     GROUPS ROUTES                    #
########################################################
@app.route('/group/create', methods=['POST'])
@login_required
def create_group():
    from app.models.group import Group

    name = request.form.get('name')
    if name is None:
        result = jsonify(status=False, error="NOT ENOUGH ARGUMENTS")
    else:
        new_group = Group.make(name)
        if new_group is None:
            result = jsonify(status=False, error="GROUP ALREADY EXISTS")
        else:
            result = jsonify(status=True)
    return result


@app.route('/group', methods=['GET'])
@login_required
def get_groups():
    from app.models.group import Group
    offset = request.args.get('offset')
    if offset is None:
        offset = 0
    return jsonify(groups=Group.parse_list(Group.get_groups(offset)), status=True)


@app.route('/group/<string:group_name>', methods=['GET'])
@login_required
def get_group_albums(group_name):
    from app.models.group import Album
    albums = Album.get_group_albums(group_name)
    if albums:
        return jsonify(status=True, albums=Album.parse_list(albums))
    else:
        return jsonify(status=False, error='GROUP DOES NOT EXIST')


########################################################
#                     ALBUM ROUTES                     #
########################################################
@app.route('/group/album/create', methods=['POST'])
@login_required
def create_album():
    from app.models.group import Album

    group_name = request.form.get('group_name')
    album_name = request.form.get('name')
    if album_name is None or group_name is None:
        result = jsonify(status=False, error="NOT ENOUGH ARGUMENTS")
    else:
        new_album = Album.make(album_name, group_name)
        if new_album is None:
            result = jsonify(status=False, error="ALBUM ALREADY EXISTS")
        else:
            result = jsonify(status=True)
    return result


@app.route('/group/<string:group_name>/<string:album_name>', methods=['GET'])
@login_required
def get_album_songs(group_name, album_name):
    from app.models.group import Song
    songs = Song.get_album_songs(group_name, album_name)
    if songs:
        return jsonify(status=True, songs=Song.parse_list(songs))
    else:
        return jsonify(status=False, error='ALBUM DOES NOT EXIST')


########################################################
#                      SONG ROUTES                     #
########################################################
@app.route('/group/album/song/create', methods=['POST'])
@login_required
def upload_song():
    from app.models.group import Song

    group_name = request.form.get('group_name')
    album_name = request.form.get('album_name')
    song_name = request.form.get('name')
    song_file = request.files.get('file')
    if album_name is None or group_name is None or song_name is None or song_file is None:
        result = jsonify(status=False, error="NOT ENOUGH ARGUMENTS")
    else:
        new_song = Song.make(song_name, album_name, group_name, song_file)
        if new_song is None:
            result = jsonify(status=False, error="SONG ALREADY EXISTS")
        else:
            result = jsonify(status=True)
    return result


@app.route('/group/<string:group_name>/<string:album_name>/<string:song_name>')
@login_required
def listen_song(group_name, album_name, song_name):
    from app.models.group import Song
    song = Song.get(song_name, album_name, group_name)
    path = song.path
    range_header = request.headers.get('Range', None)
    if not range_header:
        return send_file(path)

    size = os.path.getsize(path)
    byte1, byte2 = 0, None

    m = re.search('(\d+)-(\d*)', range_header)
    g = m.groups()

    if g[0]:
        byte1 = int(g[0])
    if g[1]:
        byte2 = int(g[1])

    length = size - byte1
    if byte2 is not None:
        length = byte2 - byte1

    with open(path, 'rb') as f:
        f.seek(byte1)
        data = f.read(length)

    rv = Response(data,
                  206,
                  mimetype=mimetypes.guess_type(path)[0],
                  direct_passthrough=True)
    rv.headers.add('Content-Range', 'bytes {0}-{1}/{2}'.format(byte1, byte1 + length - 1, size))
    rv.headers.add('Accept-Ranges', 'bytes')
    return rv

