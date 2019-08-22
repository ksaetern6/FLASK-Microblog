from flask import Blueprint


# Blueprint takes in name of blueprint and name of base module.
bp = Blueprint('errors', __name__)


# Importing handlers.py
from app.errors import handlers