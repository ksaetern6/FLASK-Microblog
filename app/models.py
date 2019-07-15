from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login
from flask_login import UserMixin
from hashlib import md5

##
# @type: class
# @name: User
# @desc: User Model for the app
## 
class User(UserMixin, db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
   
    #User Profile fields 
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    ##
    # @name: set_password
    # @desc: creates a hash of a given string and stores it in the object
    ##
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    ##
    # @name: check_password
    # @desc: return True or False on a hash of a given string
    ##
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    ##
    # @name: avatar
    # @desc: Uses Gravatar which uses hashes a user's email addr and Gravatar's
    # URL avatar link to give a profile avatar at a given size using a given 
    # parameter. Then the method returns the avatar link. If a profile does
    # not have a link then a default 'identicon' is given.
    ##
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https:www.gravatar.com/avatar/{}?id=identicon&s={}'.format(
            digest, size)
    
    #tells Python how to print objects of this class, for debugging.
    def __repr__(self):
        return '<User {}>'.format(self.username)
##
# @type class
# @name Post
# @desc blog posts written by users
##
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    #default lets SQLAlchemy set the field to the value of calling that function.
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return 'Post {}>'.format(self.body)

#user loader for Flask-Login
#id is a string that gets converted to a int for the db
@login.user_loader
def load_user(id):
    return User.query.get(int(id))
