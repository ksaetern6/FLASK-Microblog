from flask import Flask
from config import Config

app = Flask(__name__)
#Flask reading config file
#config is the name of module 'config.py' and Config is the actual class
app.config.from_object(Config)

from app import routes
