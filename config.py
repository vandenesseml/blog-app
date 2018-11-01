import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
    POST_IMAGE_UPLOAD_FOLDER = './app/static/uploads/post/'
    POST_IMAGE_ACCESS_PATH = '/static/uploads/post/'
    PROFILE_IMAGE_UPLOAD_FOLDER = './app/static/uploads/profile/'
    PROFILE_IMAGE_ACCESS_PATH = '/static/uploads/profile/'
    POSTS_PER_PAGE = 10
    COMMENTS_PER_POST = 5
