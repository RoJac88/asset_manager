from flask import Blueprint

bp = Blueprint('mailmerge', __name__)

from app.mailmerge import routes
