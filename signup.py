from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mail import Mail, Message
import os
import secrets
import hashlib
import time

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


def generate_verification_token():
    # 32바이트 길이의 무작위 토큰 생성
    token = secrets.token_hex(16)

    # 토큰에 현재 시간을 추가하여 유효 기간을 설정
    expiration_time = int(time.time()) + 3600  # 1시간 동안 유효

    # 토큰과 유효 기간을 결합하여 문자열 생성
    token_string = f'{token}.{expiration_time}'

    # 문자열을 해시화하여 보안 향상
    hashed_token = hashlib.sha256(token_string.encode()).hexdigest()

    return hashed_token


# 이메일 전송 함수
def send_verification_email(email, token):
    print(f'Token: {token}')
    subject = '이메일 인증'
    body = f'인증 링크: {url_for("verify_email", token=token, _external=True)}'
    message = Message(subject, recipients=[email], body=body)
    mail.send(message)

# 이메일 인증을 위한 데이터베이스 대신 사용할 간단한 딕셔너리
user_data = {}


# 회원 가입 시에 이메일 인증 메일 보내기
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']

        print('Email: ', email)
        # 이미 가입한 이메일인지 확인
        if email in user_data:
            flash('이미 가입된 이메일 주소입니다.', 'error')
            return redirect(url_for('signup'))

        token = generate_verification_token()
        user_data[email] = {'token': token, 'verified': False, 'timestamp': time.time()}

        # 이메일을 보내는 함수 호출
        send_verification_email(email, token)

        flash('이메일로 인증 링크가 전송되었습니다. 이메일을 확인해주세요.', 'info')
        return redirect(url_for('index'))

    return render_template('signup.html')


# 이메일 인증 페이지
@app.route('/verify/<token>')
def verify_email(token):
    print('Verifying...')
    print(user_data)
    # 토큰을 확인하고 사용자를 활성화하거나 인증 상태를 갱신하는 로직
    for email, data in user_data.items():
        if data['token'] == token and not data['verified']:
            # 토큰이 일치하고 아직 인증되지 않은 경우에만 인증
            data['verified'] = True
            flash('이메일이 성공적으로 인증되었습니다!', 'success')
            return redirect(url_for('index'))

    flash('유효하지 않은 인증 토큰입니다.', 'error')
    return redirect(url_for('index'))


# 라우트 예시
@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
