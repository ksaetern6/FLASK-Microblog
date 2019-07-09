import os

#As app needs more configuration items, they can be added to this class.
#Can also add a subclass for another configuration set
class Config(object):
    #important configuration variable for Flask apps.
    #Used for cryptographic key, useful to generate signatures or tokens.
    #SECRET_KEY value is a value sourced from an environment variable.
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
