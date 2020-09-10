from flask import Flask, url_for
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from logging.handlers import RotatingFileHandler, SMTPHandler
import os
import logging


# 创建app
app = Flask(__name__)
app.config.from_object(Config)

# 把app注册给SQLAlchemy
# 数据库操作
db = SQLAlchemy(app)

# 把app和db注册给Migrate
# 数据库版本迁移工具
migrate = Migrate(app, db)

# 把app注册给LoginManager
# 登陆管理
login = LoginManager(app)
login.login_view = 'login'
login.login_message = '0,请登录'

# 把app注册给Mail
# 邮件管理
mail = Mail(app)

from app import routes, models, errors

if not app.debug:
    
    ## log by file
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/electronic.log', maxBytes=10240,
                                       backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('Electronic startup')

    ### log by mail, it dosnot make sense
    # if app.config['MAIL_SERVER']:
    #     auth = None
    # if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
    #     auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
    # secure = None
    # if app.config['MAIL_USE_TLS']:
    #     secure = ()
    # mail_handler = SMTPHandler(
    #     mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
    #     fromaddr=app.config['MAIL_USERNAME'],
    #     toaddrs=app.config['ADMINS'], subject='Microblog Info',
    #     credentials=auth, secure=secure)
    # mail_handler.setLevel(logging.INFO)
    # app.logger.addHandler(mail_handler)

    # app.logger.info("Microblog startup")


