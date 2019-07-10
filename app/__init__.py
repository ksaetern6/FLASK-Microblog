from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
#Flask reading config file
#config is the name of module 'config.py' and Config is the actual class
app.config.from_object(Config)
##
# creating db object and migration engine object
##
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import routes, models
