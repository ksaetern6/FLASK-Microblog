import logging
import os
from logging.handlers import SMTPHandler, RotatingFileHandler
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_moment import Moment

app = Flask(__name__)
# Flask reading config file
# config is the name of module 'config.py' and Config is the actual class
app.config.from_object(Config)

##
# creating db object and migration engine object
##
db = SQLAlchemy(app)
migrate = Migrate(app, db)

##
# using flask_login package 
##
# endpoint for login view
login = LoginManager(app)
# view to require users to login to view a page
login.login_view = 'login'

##
# Flask-Mail
##
mail = Mail(app)

##
# Flask-Bootstrap
##
bootstrap = Bootstrap(app)

##
# flask-moment
##
moment = Moment(app)


##
# ERROR_HANDLING using env variables
##
if not app.debug:  # if not in debug mode
    if app.config['MAIL_SERVER']:  # if the email server exists
        auth = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        secure = None
        if app.config['MAIL_USE_TLS']:
            secure = ()
        # creates SMTPHandler, set to only report errors, not
        # warnings/debug messages. Then attached to app.logger
        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr='no-reply@' + app.config['MAIL_SERVER'],
            toaddrs=app.config['ADMINS'], subject='Microblog Failure',
            credentials=auth, secure=secure)
        mail_handler.setLevel(logging.ERROR)  # only errors reported
        app.logger.addHandler(mail_handler)

##
# LOG FILE HANDLING
##
if not app.debug:
    # writing/creating log to logs dir
    if not os.path.exists('logs'):
        os.mkdir('logs')
    # RotatingFileHandler limits log files to 10KB and keeps last 10 as backup
    file_handler = RotatingFileHandler('logs/microblog.log', maxBytes=10240,
                                       backupCount=10)
    # logging.Formatter sets the format for the log messages.
    # includes timestamp, logging level, message, and src file and line number
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    # logging level set to INFO category.
    # DEBUG > INFO > WARNING > ERROR > CRITICA
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('Microblog startup')

from app import routes, models, errors
