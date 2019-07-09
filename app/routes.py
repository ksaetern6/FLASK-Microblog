from flask import render_template, flash, redirect, url_for
from app import app
from app.forms import LoginForm

#decarators -modifies the function that follows it
#@app.route creates an association between the URL given as
#an argument and the function.

@app.route('/')
@app.route('/index')
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
    return render_template('index.html', title='Home', user=user, posts=posts)
##
# login view
# 
##
@app.route('/login', methods=['GET', 'POST'])
def login():
    # create form object and passed into render_template.
    # form on the left is the template and form on the right is created from 
    # LoginForm
    form = LoginForm()
    ##
    # if statement does the form processing.
    # GET request to receive the web page with the login form is going to 
    # return False and skip the if statement and render the form.
    # A POST request from pressing the submit button gathers the data and
    # runs the validators attached to the fields.
    # flash() shows a msg to the user and returns a redirect back to index.
    ## 
    if form.validate_on_submit():
        #Edited base.html to allow flash to appear in Flask.
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)
