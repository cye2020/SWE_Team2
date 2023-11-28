from flask import Flask
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from apscheduler.schedulers.background import BackgroundScheduler
import os


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


def create_app():
    app = Flask(__name__)

    app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'default_secret_key')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:peter0107@database-1.cc0lokhfxaeb.us-east-2.rds.amazonaws.com/software_database'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Flask-Mail 설정
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USERNAME'] = 'seongdaeuijib@gmail.com'
    app.config['MAIL_PASSWORD'] = 'tman vfxa wmiq jccb'
    app.config['MAIL_PASSWORD'] = 'rzor wmwd vaiz bidq'
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True
    app.config['MAIL_DEFAULT_SENDER'] = 'seongdaeuijib@gmail.com'
    
    login_manager.init_app(app)
    db.init_app(app)
    mail.init_app(app)
    bcrypt.init_app(app)
    cors.init_app(app)
    
    return app





