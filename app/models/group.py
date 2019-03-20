import os
import logging
from app.app import db
from app.utils.string_utils import crop_withespaces, allowed_file
from werkzeug.utils import secure_filename


class Group(db.Document):

    name = db.StringField()
    path = db.StringField()

    @staticmethod
    def make(name: str):
        new_group = None
        if Group.query.filter(Group.name == name).first() is None:
            path = './music/' + crop_withespaces(name)
            new_group = Group(name=name, path=path)
            new_group.save()
            os.mkdir(path)
        return new_group

    @staticmethod
    def get(name: str):
        return Group.query.filter(Group.name == name).first()

    def json(self):
        json_result = dict()
        json_result['name'] = self.name
        return json_result


class Album(db.Document):

    name = db.StringField()
    group = db.DocumentField(Group)
    path = db.StringField()

    @staticmethod
    def make(name: str, group_name: str):
        group = Group.get(group_name)
        new_album = None
        if group is not None and Album.query.filter(Album.name == name, Album.group == group).first() is None:
            path = group.path + '/' + crop_withespaces(name)
            new_album = Album(name=name, group=group, path=path)
            new_album.save()
            os.mkdir(path)
        return new_album

    @staticmethod
    def get(name: str, group_name: str):
        group = Group.get(group_name)
        if group:
            return Album.query.filter(Album.name == name, Album.group == group).first()
        else:
            return None

    @staticmethod
    def get_group_albums(group_name: str):
        group = Group.get(group_name)
        if group:
            return Album.query.filter(Album.group == group).all()
        else:
            return None

    @staticmethod
    def parse_list(album_list):
        result = []
        for album in album_list:
            result.append(album.json())
        return result

    def json(self):
        json_result = dict()
        json_result['name'] = self.name
        json_result['group'] = self.group.json()
        return json_result


class Song(db.Document):

    name = db.StringField()
    album = db.DocumentField(Album)
    path = db.StringField()

    @staticmethod
    def make(name: str, album_name, group_name, song_file):
        album = Album.get(album_name, group_name)
        new_song = None
        if album is not None and Song.query.filter(Song.name == name, Song.album == album).first() is None:
            logging.debug(song_file.filename)
            if allowed_file(song_file.filename):
                logging.debug("rr")
                path = album.path + '/' + secure_filename(song_file.filename)
                new_song = Song(name=name, album=album, path=path)
                new_song.save()
                song_file.save(path)
        return new_song

    @staticmethod
    def get(path: str):
        return Album.query.filter(Song.path == path).first()

    @staticmethod
    def get_album_songs(group_name: str, album_name: str):
        album = Album.get(album_name, group_name)
        if album:
            return Song.query.filter(Song.album == album).all()
        else:
            return None

    @staticmethod
    def parse_list(song_list):
        result = []
        for song in song_list:
            result.append(song.json())
        return result

    def json(self):
        json_result = dict()
        json_result['name'] = self.name
        json_result['path'] = self.path
        return json_result
