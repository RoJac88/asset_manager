import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TEMPLATES_FOLDER = os.path.join('app', 'mailmerge', 'models')
    OUTPUT_FOLDER = os.path.join('mailmerge', 'output')
    RE_FILES_FOLDER = os.path.join('app', 'realestate', 'files')
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024 # 8 megabytes
