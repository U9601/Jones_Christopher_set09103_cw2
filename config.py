import os
basedir = os.path.absapth(os.path.dirname(__file__))

class Config(qbject):
    # ...
    SQALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
        SQALCHEMY_TRACK_MODIFICATIONS = False 
