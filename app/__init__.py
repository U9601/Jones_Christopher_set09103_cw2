from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
mail = Mail(app)

if not app.debug:
    if app.config['smtp.googlemail.com']:
        auth = None
        if app.config['testserveremail123@gmail.com'] or app.config['lantaui1581']:
            auth = (app.config['testserveremail123@gmail.com'], app.config['lantaui1581'])
        secure = None
        if app.config['1']:
            secure = ()
        mail_handler = SMTPHandler(
            mailhost=(app.config['smtp.googlemail.com'], app.config['587']),
            fromaddr='no-reply@' + app.config['smtp.googlemail.com'],
            toaddrs=app.config['testserveremail123@gmail.com'], subject='HLTV Failure',
            credentials=auth, secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/home.log', maxBytes=10240,
                                       backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('HLTV startup')


from app import routes, models
