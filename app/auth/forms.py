from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, BooleanField, SubmitField,)
from wtforms.validators import (DataRequired, ValidationError, Email, EqualTo,)
from app.models import User
from flask_babel import lazy_gettext as _l


##
# @type: class
# @name: LoginForm
# @desc: 
##
class LoginForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign in')


##
# @type: class
# @name: RegistrationForms
# @desc: 
##
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    # custom validators using the validator_<name> invoke from WTForms
    ##
    # @name: validate_username
    # @desc: check if username is taken or meets requirements
    ##
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please user a different username.')

    ##
    # @name: validate_email
    # @desc: check if email is already being used
    ##
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


##
# @type: class
# @name: ResetPasswordRequestForm
# @desc: Form asks
##
class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')


##
# @type: class
# @name: ResetPasswordForm
# @desc: form with two fields to hold data for password change.
##
class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')]
    )
    submit = SubmitField('Request Password Reset')
