import os
from app.app import db
from app.utils.string_utils import crop_withespaces


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
            return Album.query.filter(Album.name == name, Album.group == group)
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
