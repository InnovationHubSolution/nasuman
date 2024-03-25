# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import Email, DataRequired

# login and registration


class LoginForm(FlaskForm):
    username = StringField('Username',
                         id='username',
                         validators=[DataRequired()])

    password = PasswordField('Password',
                             id='password',
                             validators=[DataRequired()])


class CreateAccountForm(FlaskForm):

    group = StringField('Group',
                         id='group',
                         validators=[DataRequired()])
    username = StringField('Username',
                         id='username_create',
                         validators=[DataRequired()])
    
    full_name = StringField('Full Name',
                         id='full_name',
                         validators=[DataRequired()])

    phone = StringField('Phone',
                         id='phone',
                         validators=[DataRequired()])


    email = StringField('Email',
                      id='email_create',
                      validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                             id='pwd_create',
                             validators=[DataRequired()])
