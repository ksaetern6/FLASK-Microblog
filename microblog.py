#Python script at teh top-level that defines the Flask application instance.
#'app' is a flask application and is a member of the 'app' application
from app import app, db
from app.models import User, Post

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post}
