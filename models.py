from app import db
from flask_security import UserMixin, RoleMixin

### Flask-Security ###
roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
    )

class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100), unique=True)
    description = db.Column(db.String(255))



### Any models ###
class Events(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(35))
    speaker = db.Column(db.String(70))
    description = db.Column(db.String(255))
    location = db.Column(db.String(70))
    dateStart = db.Column(db.DateTime())
    dateFinish = db.Column(db.DateTime())

    def __init__(self, *args, **kwargs):
        super(Events, self).__init__(*args, **kwargs)

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chat_id =  db.Column(db.Integer, unique=True)
    username = db.Column(db.String(70), unique=True)
    first_name = db.Column(db.String(35))
    last_name = db.Column(db.String(35))
    status = db.Column(db.String(15))
    is_confirmed = db.Column(db.Boolean(False))

    def __init__(self, *args, **kwargs):
        super(Users, self).__init__(*args, **kwargs)