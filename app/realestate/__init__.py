from flask import Blueprint

bp = Blueprint('realestate', __name__)

from app.realestate import routes
