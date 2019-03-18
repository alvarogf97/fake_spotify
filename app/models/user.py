from app.app import db


class User(db.Document):

    name = db.StringField()
    password = db.StringField()

    @staticmethod
    def make(name: str, password: str):
        new_user = None
        if User.query.filter(User.name == name).first() is None:
            new_user = User(name=name, password=password)
            new_user.save()
        return new_user

    @staticmethod
    def get(name: str, password: str):
        return User.query.filter(User.name == name, User.password == password).first()
