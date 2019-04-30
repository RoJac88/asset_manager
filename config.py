import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'marvin-e-lulu'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ITEMS_PER_PAGE = 50
    CSV_FOLDER = os.path.abspath(os.path.join('app', 'csv')) # deprecate
    TEMPLATES_FOLDER = os.path.join('app', 'mailmerge', 'models')
    OUTPUT_FOLDER = os.path.join('mailmerge', 'output')
    # Refers to mail merge templates, not jinja2 templates!
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024 # 8 megabytes
    STATIC_FOLDER = os.path.join('static')
