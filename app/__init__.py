import os

from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import logging
from logging.handlers import RotatingFileHandler
from flask_bootstrap import Bootstrap
from flask_moment import Moment

db = SQLAlchemy()
migrate = Migrate()
bootstrap = Bootstrap()
moment = Moment()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message_category = 'danger'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    bootstrap.init_app(app)
    moment.init_app(app)
    login.init_app(app)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.people import bp as people_bp
    app.register_blueprint(people_bp)

    from app.mailmerge import bp as mailmerge_bp
    app.register_blueprint(mailmerge_bp)

    from app.realestate import bp as realestate_bp
    app.register_blueprint(realestate_bp)

    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240,
                                           backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('crud app startup')

    return app

from app import models
