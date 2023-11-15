from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mail import Mail, Message
import os
from user import User, TokenManager
from apscheduler.schedulers.background import BackgroundScheduler


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
    if request.method == 'POST':
        # 회원가입 정보를 받아온다. (이메일, 비밀번호, 닉네임)
        email = request.form['email']
        password = request.form['password']
        name = request.form['name']
        
        user = User(email, password, name)
        
        # 이미 가입한 이메일인지 확인
        if user.check_registered():
            flash('이미 가입된 이메일 주소입니다.', 'error')
            return redirect(url_for('signup'))
        
        # 토큰 생성 및 이메일에 매핑
        token = token_manager.generate_token(email)

        # 이메일을 보내는 함수 호출
        send_verification_email(email, token)

        flash('이메일로 인증 링크가 전송되었습니다. 이메일을 확인해주세요.', 'info')
        return redirect(url_for('index'))

    return render_template('signup.html')


# 이메일 인증 페이지
@app.route('/verify/<token>')
def verify_email(token):
    print('Verifying...')
    
    # 토큰을 확인하고 사용자를 활성화하거나 인증 상태를 갱신하는 로직
    for email in token_manager.tokens:
        if token_manager.verify_token(email, token):
            token_manager.mark_as_verified(email)
            flash('이메일이 성공적으로 인증되었습니다!', 'success')
            return redirect(url_for('index'))

    flash('유효하지 않은 인증 토큰입니다.', 'error')
    return redirect(url_for('index'))


# 라우트 예시
@app.route('/')
def index():
    return render_template('index.html')


# Flask 애플리케이션에 스케줄러 추가
scheduler = BackgroundScheduler()
scheduler.add_job(func=token_manager.remove_expired_tokens, trigger='interval', seconds=3600)  # 1시간마다 호출
scheduler.start()


if __name__ == '__main__':
    app.run(debug=True)
