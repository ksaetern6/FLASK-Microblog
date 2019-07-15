from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

app = Flask(__name__)
#Flask reading config file
#config is the name of module 'config.py' and Config is the actual class
app.config.from_object(Config)

##
# creating db object and migration engine object
##
db = SQLAlchemy(app)
migrate = Migrate(app, db)

##
# using flask_login package 
##
#endpoint for login view
login = LoginManager(app)
#view to require users to login to view a page
login.login_view = 'login'

from app import routes, models
