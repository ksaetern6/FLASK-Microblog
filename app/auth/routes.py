from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_babel import _
from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm, \
    ResetPasswordRequestForm, ResetPasswordForm
from app.models import User
from app.auth.email import send_password_reset_email


##
# login view
# 
##
@bp.route('/login', methods=['GET', 'POST'])
def login():
    # if user is already logged in they cannot access the login page again
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    # loading login form
    form = LoginForm()

    if form.validate_on_submit():
        # result of filter_by is a query that includes the object
        # matching the username, first() returns the first from the query
        # because its either 1 or 0 results.
        user = User.query.filter_by(username=form.username.data).first()
        # if query matches no users or if password is invalid
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        # if user & password are correct login the user.
        login_user(user, remember=form.remember_me.data)
        # next_page is stored in the URL to redirect back to the original page
        # after logging in.
        next_page = request.args.get('next')
        # url_parse and netloc is used to determine if the url is relative
        # absolute so the user stays in the same site as the application.
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('auth/login.html', title=_('Sign In'), form=form)


##
# @name: register
# @desc:
##
@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(_('Congratulations, you are now a registered user!'))
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title=_('Register'),
                           form=form)


##
# @name: logout
# @desc: logs user out
##
@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))


##
# @name: reset_password_request
# @desc: create form to reset password from app.forms and grabs user form database that matches
# the form's email, then sends the email to the user's email address.
##
@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = ResetPasswordRequestForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        # a flash is sent to screen no matter if the user exists or not for security.
        flash(_('Check your email for the instructions to reset your password'))
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html', title=_('Reset Password'), form=form)


##
# @name: reset_password
# @desc: if user is verified through the token, then the password is reset in the db. Else
#   the user is redirected back to the homepage.
##
@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(_('Your password has been reset.'))
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)

