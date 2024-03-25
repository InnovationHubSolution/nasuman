from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField,PasswordField
from wtforms.validators import DataRequired, Email

class Plan(FlaskForm):
    name        = StringField('Plan Name', validators=[DataRequired()])
    price       = StringField('Price', validators=[DataRequired()])
    desciptions = StringField('Description', validators=[DataRequired()])
    submit      = SubmitField('Update')
