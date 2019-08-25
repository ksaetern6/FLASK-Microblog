from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login
from flask_login import UserMixin
from hashlib import md5
from time import time
from app.search import add_to_index, remove_from_index, query_index
from flask import current_app
import jwt

##
# @desc: Followers Association Table, not declared as a model because
#   the table has no data other than foreign keys.
##
followers = db.Table('followers',
                     db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
                     db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
                     )


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

    # User Profile fields
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    # Many-to-Many followers relationship
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    ##
    # @name: follow
    # @desc: uses relationship/application methods to add user to following list
    ##
    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    ##
    # @name: unfollow
    # @desc: uses relationship/application methods to remove user from
    #   following list.
    ##
    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    ##
    # @name: is_following
    # @desc: checks if following link exists in the database, returns 0 or 1
    #
    ##
    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0
        ##

    # @name: followed_post
    # @desc: Creates temp table from Posts and uses User's id to filter table
    #   so the table only displays posts followed by the user.
    ##
    def followed_posts(self):
        # joining Post table with 'followers' being the association table
        # and the second argument is the join condition --
        # (followers.c.followed_id == Post.user_id)
        # This join creates a temp table with combined data from Posts table
        # and followers table.
        followed = Post.query.join(
            # condition says followed_id of followers table must be equal to
            # user_id of posts table.

            # filter selects the user_id(self.id) of the current User.
            # we are only getting posts this user follows from the temp table.
            followers, (followers.c.followed_id == Post.user_id)).filter(
            followers.c.follower_id == self.id)
        # the user's own posts that are unioned with the temp table of posts
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())

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
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    ##
    # @name: get_reset_password_token
    # @desc: generates JWT token as a string and returns it.
    ##
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    # decode necessary because encode() returns token as a byte sequence, we want it as a string.

    ##
    # @name: verify_reset_password_token
    # @desc: staticmethod that can be invoked directly from the class. Method takes a token object and
    #   decodes it. If it cannot be validated or expired and an exception through the try catch is raised
    #   and returns None. Else the id of the user from the token is grabbed from the db and returned.
    ##
    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return

        return User.query.get(id)

    # tells Python how to print objects of this class, for debugging.
    def __repr__(self):
        return '<User {}>'.format(self.username)


##
# @type class
# @name SearchableMixin
# @desc
##
class SearchableMixin(object):
    # @classmethod is a special method associated with the class, not a particular instance,
    # does not need creation of class instance to call classmethod
    # 'self' renamed to 'cls' so the method receives a class and not an instance as its first argument
    # ex: 'Post.search()' w/o instance of Post object

    ##
    # @name: search
    # @para: cls, expression, page, per_page
    #   cls: class
    #   expression: what to query
    #   page: page number
    #   per_page: how many per page
    # @desc: wraps query_index() to replace list of object IDs with actual objects.
    ##
    @classmethod
    def search(cls, expression, page, per_page):
        # cls.__tablename__ = Flask-SQLAlchemy relational table name
        #  ids = list of result IDs & total = total number of results
        ids, total = query_index(cls.__tablename__, expression, page, per_page)
        if total == 0:
            return cls.query.filter_by(id=0), 0

        when = []
        for i in range(len(ids)):
            when.append((ids[i], i))

        # db.case() is used to retrieve a list of objects by their id.
        return cls.query.filter(cls.id.in_(ids)).order_by(
            db.case(when, value=cls.id)), total

    ##
    # @name: before_commit
    # @para: cls, session
    #   cls: class
    #   session: session from SQLAlchemy during a commit
    # @desc: respond to SQLAlchemy before a commit, used to figure out what objects are
    #   going to be added(add), modified(update), or deleted(delete)
    #   saved to session._changes so objects will survive the commit process and use to update elasticsearch
    ##
    @classmethod
    def before_commit(cls, session):
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

    ##
    # @name: after_commit
    # @para: cls, session
    #   cls: class
    #   session: session from SQLAlchemy during a commit
    # @desc: respond to SQLAlchemy after commit. Used to make changes to Elasticsearch side
    #   uses session._changes side created before_commit()
    ##
    @classmethod
    def after_commit(cls, session):
        for obj in session._changes['add']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        # add_to_index updates a doc if the model_id is the same
        for obj in session._changes['update']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['delete']:
            if isinstance(obj, SearchableMixin):
                remove_from_index(obj.__tablename__, obj)
        session._changes = None

    ##
    # @name: reindex
    # @desc: helper method used to add all posts in the db to the search index
    ##
    @classmethod
    def reindex(cls):
        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)


# set up event handlers to SQLAlchemy's db.event.listen() to know when there's a commit
db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)


##
# @type class
# @name Post
# @desc blog posts written by users with 5 columns
#   SearchableMixin is a Mixin class for Post.
##
class Post(SearchableMixin, db.Model):
    # class attribute that lists fields that can be searched by elasticsearch
    # In this case, it's 'body'
    __searchable__ = ['body']

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    # default lets SQLAlchemy set the field to the value of calling that function.
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    language = db.Column(db.String(5))

    def __repr__(self):
        return 'Post {}>'.format(self.body)


# user loader for Flask-Login
# id is a string that gets converted to a int for the db
@login.user_loader
def load_user(id):
    return User.query.get(int(id))
