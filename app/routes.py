from flask import render_template
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
##
@app.route('/login')
def login():
    #create form object and passed into render_template.
    #form on the left is the template and form on the right is created from LoginForm
    form = LoginForm()
    return render_template('login.html', title='Sign In', form=form)
