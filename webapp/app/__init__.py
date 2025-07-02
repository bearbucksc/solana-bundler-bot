from flask import Blueprint

bp = Blueprint('app', __name__)

from webapp.app import routes, models
