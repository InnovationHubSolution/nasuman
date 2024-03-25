# -*- encoding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField,PasswordField
from wtforms.validators import DataRequired, Email

class ProfileForm(FlaskForm):
    group = StringField('Group', render_kw={"readonly": True})
    full_name = StringField('First Name', validators=[DataRequired()])
    birthday = StringField('Birthday', validators=[DataRequired()])
    gender = SelectField('Gender', choices=[('1', 'Female'), ('2', 'Male')], validators=[DataRequired()])
    email = StringField('Email', validators=[Email()], render_kw={"readonly": True})
    phone = StringField('Phone', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    province = SelectField('Province', choices=[('',''),('Tafea', 'Tafea'), ('Shefa', 'Shefa'), ('Penama', 'Penama'), ('Malampa', 'Malampa'), ('Torba', 'Torba')], validators=[DataRequired()])
    island = SelectField('Island', choices=[('',''),('Efate', 'Efate'), ('Tanna', 'Tanna'), ('Santo', 'Santo'), ('Malekula', 'Malekula'), ('Pantecos', 'Pantecos')], validators=[DataRequired()])
    submit = SubmitField('Update')


class MemberForm(FlaskForm):
    full_name = StringField('Full Name', id="full_name", validators=[DataRequired()])
    phone = StringField('Phone', id="phone", validators=[DataRequired()])
    email = StringField('Email', id="email", validators=[DataRequired()])
    username = StringField('Username', id="username", validators=[DataRequired()])
    password = PasswordField('Password', id='password', validators=[DataRequired()])
    address = StringField('Address', id="address", validators=[DataRequired()])
    relative_name = StringField("Relative's Name", id="relative_name", validators=[DataRequired()])
    relative_phone = StringField("Relative's Phone", id="relative_phone", validators=[DataRequired()])
    relative_address = StringField("Relative's Address", id="relative_address", validators=[DataRequired()])