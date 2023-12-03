#Flask 시작 전 준비사항

from flask import Flask
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from apscheduler.schedulers.background import BackgroundScheduler
import os
from config import MAIL_SENDER, MAIL_PASSWORD, DATABASE_URI
from connection import s3_connection


# Flask-Login 초기화
login_manager = LoginManager()
login_manager.session_protection = "strong"
login_manager.login_view = "login"
login_manager.login_message_category = "info"

db = SQLAlchemy()
mail = Mail()
bcrypt = Bcrypt()
cors = CORS()

# Flask 애플리케이션에 스케줄러 추가
scheduler = BackgroundScheduler()

# AWS S3 연결
s3 = s3_connection()


def create_app():
    app = Flask(__name__)

    app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'default_secret_key')
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Flask-Mail 설정
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USERNAME'] = MAIL_SENDER
    app.config['MAIL_PASSWORD'] = MAIL_PASSWORD
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True
    app.config['MAIL_DEFAULT_SENDER'] = MAIL_SENDER
    
    login_manager.init_app(app)
    db.init_app(app)
    mail.init_app(app)
    bcrypt.init_app(app)
    cors.init_app(app)
    
    return app
