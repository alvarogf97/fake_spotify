import json
from flask import Flask, session, request, jsonify
from flask_session import Session
from flask_mongoalchemy import MongoAlchemy
from app.server_configuration import DATABASE_NAME, DATABASE_DOMAIN, DATABASE_PORT
from app.server_configuration import DATABASE_USER, DATABASE_PASSWORD
from app.server_configuration import SESSION_TYPE


app = Flask(__name__)

app.secret_key = '9W[C|i8M9iJALx8UO1nU'
app.config['SESSION_TYPE'] = SESSION_TYPE
Session(app)

app.config['MONGOALCHEMY_DATABASE'] = DATABASE_NAME
app.config['MONGOALCHEMY_SERVER'] = DATABASE_DOMAIN
app.config['MONGOALCHEMY_PORT'] = DATABASE_PORT
# app.config['MONGOALCHEMY_USER'] = DATABASE_USER
# app.config['MONGOALCHEMY_PASSWORD'] = DATABASE_PASSWORD
db = MongoAlchemy(app)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/login', methods=['POST'])
def login():
    from app.models.user import User

    name = request.form.get('name')
    password = request.form.get('password')
    result = dict()
    if name is None or password is None:
        result["status"] = False
        result["error"] = "NOT ENOUGH ARGUMENTS"
    else:
        user = User.get(name, password)
        if user is None:
            result["status"] = False
            result["error"] = "WRONG USERNAME/PASSWORD"
        else:
            result["status"] = True
            result["name"] = user.name
            session['current_user'] = user.name
    return json.dumps(result)


@app.route('/logout')
def logout():
    session.pop('current_user')


@app.route('/register', methods=['POST'])
def register():
    from app.models.user import User

    result = dict()
    name = request.form.get('name')
    password = request.form.get('password')
    if name is None or password is None:
        result["status"] = False
        result["error"] = "NOT ENOUGH ARGUMENTS"
    else:
        new_user = User.make(name, password)
        if new_user is None:
            result["status"] = False
            result["error"] = "USERNAME ALREADY EXISTS"
        else:
            result["status"] = True
            # session['current_user'] = new_user
    return json.dumps(result)
