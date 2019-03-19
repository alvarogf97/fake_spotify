from app.app import db, bcrypt


class User(db.Document):

    name = db.StringField()
    password = db.StringField()

    @staticmethod
    def make(name: str, password: str):
        new_user = None
        if User.query.filter(User.name == name).first() is None:
            password = bcrypt.generate_password_hash(password).decode('utf-8')
            new_user = User(name=name, password=password)
            new_user.save()
        return new_user

    @staticmethod
    def get(name: str, password: str):
        user = User.query.filter(User.name == name).first()
        if user is None or not bcrypt.check_password_hash(user.password, password):
            user = None
        return user
