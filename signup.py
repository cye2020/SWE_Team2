from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mail import Mail, Message
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from apscheduler.schedulers.background import BackgroundScheduler
import os
from user import User, TokenManager



app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'default_secret_key')

# Flask-Mail 설정
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'yourmail@gmail.com'
app.config['MAIL_PASSWORD'] = 'your_password'  # 여기에 생성된 앱 비밀번호를 입력하세요.
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_DEFAULT_SENDER'] = 'yourmail@gmail.com'

mail = Mail(app)

# Flask-Login 초기화
login_manager = LoginManager(app)
login_manager.login_view = 'login'


# 회원 가입 폼 정의 (Flask-WTF 사용)
class SignupForm(FlaskForm):
    email = StringField('이메일', validators=[DataRequired(), Email()])
    password = PasswordField('비밀번호', validators=[DataRequired()])
    confirm_password = PasswordField('비밀번호 확인', validators=[DataRequired(), EqualTo('password')])
    nickname = StringField('닉네임', validators=[DataRequired()])
    submit = SubmitField('가입하기')
    
    
# 이메일 전송 함수
def send_verification_email(email, token):
    subject = '이메일 인증'
    body = f'인증 링크: {url_for("verify_email", token=token, _external=True)}'
    message = Message(subject, recipients=[email], body=body)
    mail.send(message)

# TokenManager 인스턴스 생성
token_manager = TokenManager()


# 회원 가입 시에 이메일 인증 메일 보내기
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        nickname = form.nickname.data

        user = User(email, password, nickname)

        if user.check_registered():
            flash('이미 가입된 이메일 주소입니다.', 'error')
            return redirect(url_for('signup'))

        token = token_manager.generate_token(email, password, nickname)

        send_verification_email(email, token)

        flash('이메일로 인증 링크가 전송되었습니다. 이메일을 확인해주세요.', 'info')
        return redirect(url_for('index'))

    return render_template('signup.html', form=form)


# 이메일 인증 페이지
@app.route('/verify/<token>')
@login_required
def verify_email(token):
    if current_user.is_authenticated:
        email = current_user.email
    
        if token_manager.verify_token(email, token):
            token_manager.mark_as_verified(email)
            
            # 사용자 정보를 가져와서 등록
            user_info = token_manager.tokens[email]['user_info']
            user = User(email, user_info['password'], user_info['name'])
            user.register()
            
            flash('이메일이 성공적으로 인증되었습니다!', 'success')
            
        else:
            flash('유효하지 않은 인증 토큰입니다.', 'error')

    return redirect(url_for('index'))


@login_manager.user_loader
def load_user(email):
    # 사용자 정보를 데이터베이스 등에서 가져오는 로직을 여기에 추가
    return User(email, '', '')


@app.route('/login', methods=['GET', 'POST'])
def login():
    # 로그인 폼 구현 (Flask-WTF 사용)
    class LoginForm(FlaskForm):
        email = StringField('이메일', validators=[DataRequired(), Email()])
        password = PasswordField('비밀번호', validators=[DataRequired()])
        submit = SubmitField('로그인')

    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User(email, password)

        if user.login():
            login_user(user, remember=True)
            flash('로그인 성공!', 'success')
            return redirect(url_for('index'))
        else:
            flash('로그인 실패. 이메일 또는 비밀번호를 확인해주세요.', 'error')

    return render_template('login.html', form=form)


# 로그아웃 라우트 추가
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('로그아웃 되었습니다.', 'info')
    return redirect(url_for('index'))


@app.route('/')
@login_required
def index():
    return render_template('index.html')


# Flask 애플리케이션에 스케줄러 추가
scheduler = BackgroundScheduler()
scheduler.add_job(func=token_manager.remove_expired_tokens, trigger='interval', seconds=3600)  # 1시간마다 호출
scheduler.start()


if __name__ == '__main__':
    app.run(debug=True)
