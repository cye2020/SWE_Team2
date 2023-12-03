# 실행파일

from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from botocore.exceptions import NoCredentialsError
from init import login_manager, scheduler, db, bcrypt, s3, create_app
from forms import RegisterForm, LoginForm
from geopy.distance import geodesic
from io import BytesIO
from token_manager import TokenManager
from mail import send_verification_email
from models import Member, House, free_post, contract_post
from config import BUCKET_NAME


application = create_app()

# TokenManager 인스턴스 생성
token_manager = TokenManager()


############## House ##################

#부동산페이지
@application.route('/house')
@login_required
def house():
    return render_template('real.html') 

@application.route('/house/filter', methods=['GET'])
def filter_houses():
    try:
        if 'reset' in request.args:
            # 전체 데이터를 반환
            all_houses = House.query.all()
            result = [
                {
                    'house_id': house.house_id,
                    'house_type': house.house_type,
                    'pay_type': house.pay_type,
                    'lat': house.lat,
                    'lon': house.lon,
                    'feature': house.feature,
                    'direction': house.direction,
                    'floor': house.floor,
                    'prc': house.prc,
                    'rentprc': house.rentprc,
                    'space1': house.space1,
                    'space2': house.space2,
                    'taglist': house.taglist,
                    'imgurl': house.imgurl
                }
                for house in all_houses
            ]

            house_type_filters = []
            pay_type_filters = []
            prc_filter = None
            rentprc_filter = None
            space2_filter = None
            taglist_filter = None
            direction_filter = None

            query = House.query.filter(House.house_type.in_(house_type_filters))
        
        else:
            # 필터 기준을 받아오기
            house_type_filters = request.args.getlist('house_type[]')
            print(f"Filters: {house_type_filters}")
            print(f"Args: {request.args}")
            pay_type_filters = request.args.getlist('pay_type[]')
            prc_filter = request.args.get('prc_lt[]')
            rentprc_filter = request.args.get('rentprc_lt[]')
            space2_filter = request.args.get('space2_lt[]')
            taglist_filter = request.args.get('taglist[]')
            direction_filter = request.args.get('direction[]')

            print("not reset")

            # 필터 조건에 따라 쿼리 작성
            query = House.query

            # 중복 선택 가능 영역
            if house_type_filters:
                query = query.filter(House.house_type.in_(house_type_filters))
                print(query)
            if pay_type_filters:
                query = query.filter(House.pay_type.in_(pay_type_filters))

            # 단일 선택(문자열)
            if direction_filter:
                query = query.filter(House.direction == direction_filter)
            if taglist_filter:
                query = query.filter(House.taglist.contains([taglist_filter]))

            # 단일 선택(숫자값 이하)
            if prc_filter:
                query = query.filter(House.prc <= int(prc_filter))
            if rentprc_filter:
                query = query.filter(House.rentprc <= int(rentprc_filter))
            if space2_filter:
                query = query.filter(House.space2 <= int(space2_filter))

            # 정렬 기준에 따라 쿼리 작성
            # if 'sort' in request.args:
            #     sort_by = request.args.get('sort[]')
            #     if sort_by == 'prc': # /filter?sort=prc&order=(ascend)or(descend)
            #         # prc가 0보다 큰 경우에만 정렬 수행, prc가 0인 경우 전세임.
            #         query = query.filter(House.prc > 0)
            #         query = query.order_by(House.prc.asc() if request.args.get('order[]') != 'descend' else House.prc.desc())
            #     elif sort_by == 'rentprc':
            #         query = query.order_by(House.rentprc.asc() if request.args.get('order[]') != 'descend' else House.rentprc.desc())
            #     elif sort_by == 'space2':
            #         query = query.order_by(House.space2.asc() if request.args.get('order[]') != 'descend' else House.space2.desc())

            # 필터된 매물 정보를 JSON 형태로 변환하여 반환
            result = []
            filtered_houses = query.all()
            for house in filtered_houses:
                result.append({
                    'house_id': house.house_id,
                    'house_type': house.house_type,
                    'pay_type': house.pay_type,
                    'lat': house.lat,
                    'lon': house.lon,
                    'feature': house.feature,
                    'direction': house.direction,
                    'floor': house.floor,
                    'prc': house.prc,
                    'rentprc': house.rentprc,
                    'space1': house.space1,
                    'space2': house.space2,
                    'taglist': house.taglist,
                    'imgurl': house.imgurl
                })
            application.logger.info(f"받은 매개변수: {request.args}")
            print(query)
            print("filtered")

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)})

#매물 세부정보 페이지 
@application.route('/house/<house_id>', methods=['GET'])
def get_house_details(house_id):
    house = House.query.filter_by(house_id=house_id).first()
    # 매물의 위치
    house_location = (house.lat, house.lon)

    # 도서관의 위치
    library_location = (37.293938, 126.975056)

    # 성균관대역의 위치
    station_location = (37.300316, 126.971163)

    # 거리 계산
    library_distance = round(geodesic(house_location, library_location).meters)
    station_distance = round(geodesic(house_location, station_location).meters)

    if house:
        return render_template('house_details.html', house=house, library_distance=library_distance, station_distance=station_distance)
    else:
        return jsonify({'error': 'House not found'}), 404 

@application.route('/house/init', methods=['GET'])
def initial():
    try:
        # 전체 주소를 가져오기
        all_houses = House.query.all()

        # 모든 주소를 JSON 형태로 변환하여 반환
        result = []
        for house in all_houses:
            result.append({
                'house_id': house.house_id,
                'house_type': house.house_type,
                'pay_type': house.pay_type,
                'lat': house.lat,
                'lon': house.lon,
                'feature': house.feature,
                'direction': house.direction,
                'floor': house.floor,
                'prc': house.prc,
                'rentprc': house.rentprc,
            })
        application.logger.info("전체 매물 정보를 가져왔습니다.")

        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)})
    
############## Board ##################

#게시판페이지
@application.route('/board')
@login_required
def board():
    try:

        free_posts = free_post.query.order_by(free_post.create_date.desc()).all()
        contract_posts= contract_post.query.order_by(contract_post.create_date.desc()).all()

        return render_template("bulletin.html",free_posts=free_posts,contract_posts=contract_posts)
    except:
        return render_template("bulletin.html")
#POST 게시물 DB(post)에 저장(완료)
@application.route('/free/post', methods=['POST'])
def post_free():
    #title과 content 가져오기
    title=request.form.get('title')
    is_anonymous = 'anon' in request.form
    content=request.form.get('content')
    create_date=request.form.get('timestamp')

    
    
    

    #DB에 저장할 board_post 객체 생성
    new_post=free_post(title=title,content=content, anon=is_anonymous,create_date=create_date,nickname=current_user.nickname)
    
    db.session.add(new_post)
    db.session.commit()  
    return redirect(url_for('board'))


#POST 게시물 DB(contract_post)에 저장(완료)
@application.route('/contract/post', methods=['POST'])
def post_contract():
    #title과 content 가져오기
    title=request.form.get('title')
    is_anonymous = 'anon' in request.form
    content=request.form.get('content')
    object=request.form.get('object')
    price=request.form.get('price')
    create_date=request.form.get('timestamp')
    
    
    

    #DB에 저장할 board_post 객체 생성
    new_post=contract_post(title=title,content=content,price=price, anon=is_anonymous,create_date=create_date,nickname=current_user.nickname)
    
    db.session.add(new_post)
    db.session.commit()
    return redirect(url_for('board'))
    
    


@application.route('/move/<string:topic>', methods=['GET'])
def move(topic):
    

    return render_template('notification.html',topic=topic)



############## Login ##################
@login_manager.user_loader
def load_user(login_id):
    return db.session.get(Member, login_id)

# Login route
@application.route("/login/", methods=("GET", "POST"), strict_slashes=False)
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        user = Member.query.filter_by(login_id=email).first()
        login_user(user, remember=True)
        return redirect(url_for('index'))
    return render_template("login.html",form=form)


# Register route
@application.route("/register/", methods=("GET", "POST"), strict_slashes=False)
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data + "@g.skku.edu"
        password = form.password.data
        nickname = form.nickname.data
        profile_image = form.profile_image.data
        filename = None
        
        if profile_image:
            filename = profile_image.filename
            
            profile_image_contents = BytesIO()
            profile_image_contents.write(profile_image.read())
            profile_image_contents.seek(0)
        
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = Member(login_id=email, password=hashed_password, nickname=nickname, profile_image=filename)
        token = token_manager.generate_token(user, profile_image_contents)

        send_verification_email(email, token)

        flash('이메일로 인증 링크가 전송되었습니다. 이메일을 확인해주세요.', 'info')
        return redirect(url_for('register'))
    return render_template("register.html",form=form)


# 이메일 인증 페이지
@application.route('/verify/<token>')
def verify_email(token):

    if token_manager.verify_token(token):
        token_manager.mark_as_verified(token)
        
        # 사용자 정보를 가져와서 등록
        user = token_manager.tokens[token]['user']
        profile_image = token_manager.tokens[token]['profile_image']
        
        # 프로필 이미지를 업로드하고 S3에 저장
        if profile_image:
            profile_image_filename = secure_filename(secure_filename(user.profile_image))
            profile_image_key = f"SWE2023_Team2/profile/{user.login_id}_{profile_image_filename}"

            try:
                s3.upload_fileobj(profile_image, BUCKET_NAME, profile_image_key)
                user.profile_image = f"https://{BUCKET_NAME}.s3.amazonaws.com/{profile_image_key}"
                db.session.add(user)
                db.session.commit()
            except NoCredentialsError:
                flash('AWS credentials not available.', 'error')
                return redirect(url_for('register'))


        message = '이메일이 성공적으로 인증되었습니다!'
        alert_type = 'success'
        return render_template('alert.html', message=message, alert_type=alert_type, redirect_url=url_for('login'))
    else:
        message = '유효하지 않은 인증 토큰입니다.'
        alert_type = 'error'
        return render_template('alert.html', message=message, alert_type=alert_type, redirect_url=url_for('register'))


# login_required로 요청된 기능에서 현재 사용자가 로그인되어 있지 않은 경우
# unauthorized 함수를 실행한다.
@login_manager.unauthorized_handler
def unauthorized():
    # 로그인되어 있지 않은 사용자일 경우 첫화면으로 이동
    return redirect(url_for('index'))


# 프로필 변경 페이지
@application.route('/profile', methods=['GET', 'POST'])
@login_required
def update_profile():
    if request.method == 'POST':
        new_nickname = request.form.get('nickname')
        new_password = request.form.get('password')

        if new_nickname:
            current_user.nickname = new_nickname
            db.session.commit()

        if new_password:
            current_user.password = bcrypt.generate_password_hash(new_password).decode('utf-8')
            db.session.commit()

        flash('프로필이 성공적으로 변경되었습니다!', 'success')
        return redirect(url_for('update_profile'))

    return render_template('')


# 로그아웃 라우트 추가
@application.route('/logout')
@login_required
def logout():
    logout_user()
    flash('로그아웃 되었습니다.', 'info')
    return redirect(url_for('index'))


# 회원 탈퇴 기능
@application.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    # 로그인된 사용자를 데이터베이스에서 삭제
    db.session.delete(current_user)
    db.session.commit()

    logout_user()  # 로그아웃
    flash('로그아웃이 완료되었습니다.', 'success')
    return redirect(url_for('index'))

@application.route('/home')
@login_required
def home():
    return render_template('home.html')

@application.route('/profile_page')
@login_required
def profile_page():
    return render_template('profile.html')
  
@application.route('/set')
@login_required
def set():
    return render_template('information.html')
# Home route
@application.route("/", methods=("GET", "POST"), strict_slashes=False)
def index():
    return render_template("userauth.html",title="Home")


# Flask 애플리케이션에 스케줄러 추가
scheduler.add_job(func=token_manager.remove_expired_tokens, trigger='interval', seconds=3600)  # 1시간마다 호출
scheduler.start()


if __name__ == '__main__':
    application.run(debug=True)
