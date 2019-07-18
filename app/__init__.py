import logging
from logging.handlers import SMTPHandler
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

##
# ERROR_HANDLING using env variables
##
if not app.debug: #if not in debug mode
    if app.config['MAIL_SERVER']: #if the email server exists
        auth = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        secure = None
        if app.config['MAIL_USE_TLS']:
            secure = ()
        #creates SMTPHandler, set to only report errors, not 
        #warnings/debug messages. Then attached to app.logger
        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr='no-reply@' + app.config['MAIL_SERVER'],
            toaddrs=app.config['ADMINS'], subject='Microblog Failure',
            credentials=auth, secure=secure)
        mail_handler.setLevel(logging.ERROR) #only errors reported
        app.logger.addHandler(mail_handler)

from app import routes, models, errors
