import os
basedir = os.path.abspath(os.path.dirname(__file__))

#As app needs more configuration items, they can be added to this class.
#Can also add a subclass for another configuration set
class Config(object):
    #important configuration variable for Flask apps.
    #Used for cryptographic key, useful to generate signatures or tokens.
    #SECRET_KEY value is a value sourced from an environment variable.
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

    ##
    #SQLAlchemy
    # SQLALCHEMY_DATABASE_URI is the location of the database using an
    # enviornment variable
    ##
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    #ERROR_HANDLING EMAIL
    MAIL_SERVER = os.environ.get('MAIL_SERVER') #server
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25) #port or port 25
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None #enryption
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') #username
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') #password
    ADMINS = ['kensdevacc@gmail.com'] #emails receiving errors
