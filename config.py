import os

basedir = os.path.abspath(os.path.dirname(__file__))

def get_avatars():
    avatars = {}
    index = 0
    root_dir = os.path.join('app', 'static', 'avatars')
    for (root, dirs, files) in os.walk(root_dir):
        for file in files:
            if file[-4:] == '.png':
                avatars[index] = 'avatars/' + file
                print('Avatar {} added: {}'.format(index, file))
                index += 1
    print(avatars)
    return avatars

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TEMPLATES_FOLDER = os.path.join('app', 'mailmerge', 'models')
    OUTPUT_FOLDER = os.path.abspath(os.path.join('app', 'mailmerge', 'output'))
    RE_FILES_FOLDER = os.path.join('app', 'realestate', 'files')
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024 # 8 megabytes
    AVATARS = get_avatars()
