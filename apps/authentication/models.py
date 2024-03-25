# -*- encoding: utf-8 -*-

from flask_login import UserMixin
from sqlalchemy.orm import relationship
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin
from apps import db, login_manager
import secrets
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

class Administrator(db.Model, UserMixin):
    __tablename__   = 'Administrator'
    id              = db.Column(db.Integer, primary_key=True)
    username        = db.Column(db.String(64), unique=True)
    full_name       = db.Column(db.String(64), unique=True)
    email           = db.Column(db.String(64), unique=True)
    password        = db.Column(db.String(64))
    phone           = db.Column(db.String(15), nullable=True)
    address         = db.Column(db.String(255), nullable=True)
    province        = db.Column(db.String(100), nullable=True)
    profile_image   = db.Column(db.String(64), unique=True)
    cover_image     = db.Column(db.String(64), unique=True)
    role            = db.Column(db.String(64), unique=True)

    def __repr__(self):
        return str(self.username)

class Users(db.Model, UserMixin):
    __tablename__   = 'Users'
    id              = db.Column(db.Integer, primary_key=True)
    username        = db.Column(db.String(64), unique=True)
    full_name       = db.Column(db.String(64), unique=True)
    email           = db.Column(db.String(64), unique=True)
    password        = db.Column(db.String(64))
    group_id        = db.Column(db.Integer, db.ForeignKey('group.id'))
    group           = relationship("Group", back_populates="users")
    phone           = db.Column(db.String(15), nullable=True)
    address         = db.Column(db.String(255), nullable=True)
    province        = db.Column(db.String(100), nullable=True)
    island          = db.Column(db.String(100), nullable=True)
    profile_image   = db.Column(db.String(64), unique=True)
    cover_image     = db.Column(db.String(64), unique=True)
    adminaccount_id = db.Column(db.Integer, db.ForeignKey('adminaccount.id'))
    subscription_id = db.Column(db.Integer, db.ForeignKey('Subscription.id'))
    subscription    = relationship("Subscription", back_populates="users")
    adminaccount    = relationship("Adminaccount", back_populates="users")

    def __repr__(self):
        return str(self.username)


@login_manager.user_loader
def user_loader(id):
    return Users.query.filter_by(id=id).first()


@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    user = Users.query.filter_by(username=username).first()
    return user if user else None

class OAuth(OAuthConsumerMixin, db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey("Users.id", ondelete="cascade"), nullable=False)
    user = db.relationship(Users)


class Group(db.Model):
    id                              = db.Column(db.Integer, primary_key=True)
    full_name                       = db.Column(db.String(100), nullable=False)
    group_name                      = db.Column(db.String(100), nullable=False)
    confirmed                       = db.Column(db.Boolean, default=False)
    confirmation_token              = db.Column(db.String(100), unique=True)
    confirmation_token_expiration   = db.Column(db.DateTime)
    users                           = relationship("Users", back_populates="group")
    members                         = relationship("Member", back_populates="group")

    def __init__(self, group_name, full_name):
        self.group_name     = group_name
        self.full_name      = full_name
        self.generate_confirmation_token()

    def generate_confirmation_token(self):
        self.confirmation_token             = secrets.token_urlsafe(32)
        self.confirmation_token_expiration  = datetime.utcnow() + timedelta(hours=1)

    def confirm(self, token):
        if self.confirmation_token == token and datetime.utcnow() < self.confirmation_token_expiration:
            self.confirmed = True
            return True
        return False

    def __repr__(self):
        return f"Group('{self.group_name}', '{self.admin_name}')"

class Member(db.Model):
    id                  = db.Column(db.Integer, primary_key=True)
    full_name           = db.Column(db.String(100), nullable=False)
    phone               = db.Column(db.String(15), nullable=False)
    address             = db.Column(db.String(255), nullable=False)
    email               = db.Column(db.String(255), nullable=False)
    username            = db.Column(db.String(100), nullable=False)
    password            = db.Column(db.String(100), nullable=False)
    relative_name       = db.Column(db.String(100), nullable=False)
    relative_phone      = db.Column(db.String(100), nullable=False)
    relative_address    = db.Column(db.String(100), nullable=False)
    group_id            = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    group               = relationship("Group", back_populates="members")

    def __repr__(self):
        return f"Member('{self.name}', '{self.full_name}')"
    


class Memberaccount(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    date            = db.Column(db.String(100), nullable=False)
    amount          = db.Column(db.Integer)
    total           = db.Column(db.Integer)
    member          = db.Column(db.Integer, db.ForeignKey('member.id'))
    lending         = db.Column(db.Integer)
    interestrate    = db.Column(db.Integer)
    repaymentdate   = db.Column(db.String(15))
    
    def __repr__(self):
        return f"Account('{self.id}', '{self.date}')"
    

class Adminaccount(db.Model):
    id      = db.Column(db.Integer, primary_key=True)
    date    = db.Column(db.String(100), nullable=False)
    amount  = db.Column(db.Integer)
    total   = db.Column(db.Integer)
    users   = relationship("Users", back_populates="adminaccount")
    def __repr__(self):
        return f"Adminaccount('{self.id}', '{self.users}')"
    

class Subscription(db.Model):
    __tablename__   = 'Subscription'
    id              = db.Column(db.Integer, primary_key=True)
    name            = db.Column(db.String(100), nullable=False)
    price           = db.Column(db.Integer)
    users           = relationship("Users", back_populates="subscription")
    purchagedate    = db.Column(db.String(100))

    def __repr__(self):
        return f"Subscription('{self.id}', '{self.name}')"

