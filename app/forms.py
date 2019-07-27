from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, BooleanField, SubmitField,
                     TextAreaField, SubmitField,
                     )
from wtforms.validators import (DataRequired, ValidationError, Email, EqualTo,
                                Length,
                                )
from app.models import User


##
# @type: class
# @name: LoginForm
# @desc: 
##
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
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
# @name: EditProfileForm
# @desc: Form that has 2 fields and a submit that allows the user to describe 
#   themselves.
##
class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')


##
# @type: class
# @name: PostForm
# @desc: Form that has a 140char textfield with a submit button.
##
class PostForm(FlaskForm):
    post = TextAreaField('Say something', validators=[
        DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('Submit')


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
