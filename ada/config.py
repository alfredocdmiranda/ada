import os
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'ada.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_TRACK_MODIFICATIONS = True

WTF_CSRF_ENABLED = True
SECRET_KEY = 'iashdasdhjqwehiqweh98123e8ucy6!&*!%!'
