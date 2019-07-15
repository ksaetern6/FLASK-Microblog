from flask import render_template, flash, redirect, url_for, request
from app import app
from app.forms import LoginForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User
from werkzeug.urls import url_parse

#decarators -modifies the function that follows it
#@app.route creates an association between the URL given as
#an argument and the function.

@app.route('/')
@app.route('/index')
@login_required
def index():
    user = {'username': 'Miguel'}
    posts = [
        {
            'author':{'username':'John'},
            'body':'Beautiful day in Portland!'
        },
        {
            'author':{'username':'Susan'},
            'body':'The Avengers movie was so cool!'
        }
    ]
    return render_template('index.html', title='Home Page',  posts=posts)
##
# login view
# 
##
@app.route('/login', methods=['GET', 'POST'])
def login():
    #if user is already logged in they cannot access the login page again
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    #loading login form
    form = LoginForm()
    #
    if form.validate_on_submit():
        #result of filter_by is a query that includes the object 
        #matching the username, first() returns the first from the query
        #because its either 1 or 0 results.
        user = User.query.filter_by(username=form.username.data).first()
        #if query matches no users or if password is invalid
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        #if user & password are correct login the user.
        login_user(user, remember=form.remember_me.data)
        #next_page is stored in the URL to redirect back to the original page 
        #after logging in.
        next_page = request.args.get('index')
        #url_parse and netloc is used to determine if the url is relative
        #absolute so the user stays in the same site as the application.
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

##
# @name: logout
# @desc: logs user out
##
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
