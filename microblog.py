# Python script at the top-level that defines the Flask application instance.
# 'app' is a flask application and is a member of the 'app' application
from app import create_app, db, cli
from app.models import User, Post


# taken from __init__.py, registers all packages
app = create_app()
cli.register(app)


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post}
