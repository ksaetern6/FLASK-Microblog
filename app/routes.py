from flask import render_template, flash, redirect, url_for, request, g
from app import app, db
from app.forms import (LoginForm, RegistrationForm, EditProfileForm, PostForm, ResetPasswordRequestForm,
                       ResetPasswordForm,
                        )
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Post
from werkzeug.urls import url_parse
from datetime import datetime
from app.email import send_password_reset_email
from flask_babel import get_locale


# decorators -modifies the function that follows it
# @app.route creates an association between the URL given as
# an argument and the function.

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        # standard to respond to a POST submission to redirect, helps mitigate
        # refresh command in web browsers.
        return redirect(url_for('index'))
    # return list of all posts that current_user follows.
    posts = current_user.followed_posts().all()

    # pagination
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page, app.config['POSTS_PER_PAGE'], False)

    next_url = url_for('index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) \
        if posts.has_prev else None

    # posts.items is a list of items in the requested page
    return render_template('index.html', title='Home Page', form=form,
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)


##
# login view
# 
##
@app.route('/login', methods=['GET', 'POST'])
def login():
    # if user is already logged in they cannot access the login page again
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    # loading login form
    form = LoginForm()
    #
    if form.validate_on_submit():
        # result of filter_by is a query that includes the object
        # matching the username, first() returns the first from the query
        # because its either 1 or 0 results.
        user = User.query.filter_by(username=form.username.data).first()
        # if query matches no users or if password is invalid
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        # if user & password are correct login the user.
        login_user(user, remember=form.remember_me.data)
        # next_page is stored in the URL to redirect back to the original page
        # after logging in.
        next_page = request.args.get('index')
        # url_parse and netloc is used to determine if the url is relative
        # absolute so the user stays in the same site as the application.
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


##
# @name: register
# @desc:
##
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


##
# @name: logout
# @desc: logs user out
##
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


##
# @name: user
# @desc: the user's profile page
##
@app.route('/user/<username>')  # < > is dynamic for Flask.
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)

    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)

    next_url = url_for('user', username=user.username, page=posts.next_num) \
        if posts.has_next else None

    prev_url = url_for('user', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None

    return render_template('user.html', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url)


##
# @name: before_request
# @desc: method executes before the view function
##
@app.before_request
def before_request():
    if current_user.is_authenticated:
        # current_user grabs the user from the db into the current db session so
        # we don't need to to db.sesson.add().
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
    # get_locale returns locale object, then converted to a string so we'll have
    # the language code.
    g.locale = str(get_locale())


##
# @name: edit_profile
# @desc: 
##
@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    # if form returns True, data gets transferred into the user object and
    # saved into the db
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved')
        return redirect(url_for('edit_profile'))
    # if GET request, popualte form with data from db
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    # if a POST but data is invalid rerender the template with failed validation
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)


##
# @name: follow
# @desc: finds user in db and follows and the current_user follows them.
##
@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are following {}!'.format(username))
    return redirect(url_for('user', username=username))


##
# @name: unfollow
# @desc: finds username in db and unfollows them from current user.
##
@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following {}.'.format(username))
    return redirect(url_for('user', username=username))

##
# @name: explore
# @desc: a view that shows all the recent posts made by users. 'index.html'
#   is still used as the template but form is redacted.
##
@app.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('explore', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title='Explore', posts=posts.items,
                           next_url=next_url, prev_url=prev_url)

##
# @name: reset_password_request
# @desc: create form to reset password from app.forms and grabs user form database that matches
# the form's email, then sends the email to the user's email address.
##
@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = ResetPasswordRequestForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        # a flash is sent to screen no matter if the user exists or not for security.
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html', title='Reset Password', form=form)


##
# @name: reset_password
# @desc: if user is verified through the token, then the password is reset in the db. Else
#   the user is redirected back to the homepage.
##
@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)

