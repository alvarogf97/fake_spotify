from app.app import db
from flask import jsonify


class Group(db.Document):

    name = db.StringField()

    @staticmethod
    def make(name: str):
        new_group = None
        if Group.query.filter(Group.name == name).first() is None:
            new_group = Group(name=name)
            new_group.save()
        return new_group

    @staticmethod
    def get(name: str):
        return Group.query.filter(Group.name == name).first()

    def jsonify(self):
        return jsonify(name=self.name)


class Album(db.Document):

    name = db.StringField()
    group = db.DocumentField(Group)

    @staticmethod
    def make(name: str, group_name: str):
        group = Group.get(group_name)
        new_album = None
        if group is not None and Album.query.filter(Album.name == name, Album.group == group).first() is None:
            new_album = Album(name=name, group=group)
            new_album.save()
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
            return Album.query.filter(Album.group == group).first()
        else:
            return None

    def jsonify(self):
        return jsonify(name=self.name, group=self.group.jsonify())
