from flask import render_template, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from init import login_manager, scheduler, db, create_app
from forms import RegisterForm, LoginForm
from token_manager import TokenManager
from mail import send_verification_email
from models import Member


app = create_app()

# TokenManager 인스턴스 생성
token_manager = TokenManager()



@login_manager.user_loader
def load_user(user_id):
    return Member.query.get(str(user_id))


# Home route
@app.route("/", methods=("GET", "POST"), strict_slashes=False)
def index():
    return render_template("index.html",title="Home")


# Login route
@app.route("/login/", methods=("GET", "POST"), strict_slashes=False)
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        user = Member.query.filter_by(login_id=email).first()
        login_user(user, remember=True)
        return redirect(url_for('index'))
    return render_template("auth.html",form=form)


# Register route
@app.route("/register/", methods=("GET", "POST"), strict_slashes=False)
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        nickname = form.nickname.data

        user = Member(login_id=email, password=password, nickname=nickname)
        token = token_manager.generate_token(user)

        send_verification_email(email, token)

        flash('이메일로 인증 링크가 전송되었습니다. 이메일을 확인해주세요.', 'info')
        return redirect(url_for('register'))
    return render_template("auth.html",form=form)


# 이메일 인증 페이지
@app.route('/verify/<token>')
def verify_email(token):

    if token_manager.verify_token(token):
        token_manager.mark_as_verified(token)
        
        # 사용자 정보를 가져와서 등록
        user = token_manager.tokens[token]['user']
        print('Member DB: Success')
        db.session.add(user)
        db.session.commit()
        flash('이메일이 성공적으로 인증되었습니다!', 'success')
    else:
        flash('유효하지 않은 인증 토큰입니다.', 'error')

    return redirect(url_for('register'))


# login_required로 요청된 기능에서 현재 사용자가 로그인되어 있지 않은 경우
# unauthorized 함수를 실행한다.
@login_manager.unauthorized_handler
def unauthorized():
    # 로그인되어 있지 않은 사용자일 경우 첫화면으로 이동
    return redirect("/")


# 로그아웃 라우트 추가
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('로그아웃 되었습니다.', 'info')
    return redirect(url_for('index'))


# Flask 애플리케이션에 스케줄러 추가
scheduler.add_job(func=token_manager.remove_expired_tokens, trigger='interval', seconds=3600)  # 1시간마다 호출
scheduler.start()


if __name__ == '__main__':
    app.run(debug=True)
