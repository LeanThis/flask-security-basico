# -*- coding: utf-8 -*-
import os
import datetime
from flask import Flask, render_template
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, login_required
from flask_mail import Mail

# Create app
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'super-secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'

app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_CONFIRMABLE'] = True
app.config['SECURITY_RECOVERABLE'] = True


# Por defecto sobre gmail
# Se puede utilizar cualquier cuenta de gmail u otra configuración
app.config['MAIL_SERVER'] = os.environ.get('SEC_MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = os.environ.get('SEC_MAIL_PORT', 465)
app.config['MAIL_USE_SSL'] = os.environ.get('SEC_MAIL_SSL', True)
app.config['MAIL_USERNAME'] = os.environ.get('SEC_MAIL_USER')
app.config['MAIL_PASSWORD'] = os.environ.get('SEC_MAIL_PASS')

mail = Mail(app)


# Create database connection object
db = SQLAlchemy(app)

# Define models
roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

# Create a user to test with
@app.before_first_request
def create_user():
    db.create_all()
    user_datastore.create_user(email='ejemplo@mail.com', password='aaaaaa', confirmed_at=datetime.datetime.now())
    db.session.commit()

# Views
@app.route('/')
@login_required
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run()