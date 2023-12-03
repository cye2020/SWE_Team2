# SWE_Team2
SKKU Introduction to Software Engineering Team 2 Project "구해봐요 성대에 집"

## 프로젝트 소개
성균관대 학생들을 위한 주거공간 커뮤니티

## 멤버 구성
* Frontend(작성요망)
    * 김강산
    * 인진영
    * 정안승 : 웹페이지 디자인, 로그인 및 회원가입 frontend 구현
    * 한재웅

* Backend
    * 강준모: 게시판 기능 backend 구현
    * 문보현: 부동산 기능 frontend, backend 구현
    * 조예은: 로그인 및 회원가입 backend 구현
    * 진송찬: document 작성 및 presentation 수행

## 개발 환경
* HTML, CSS
* JavaScript
* AWS(MySQL)
* Flask

## 프로젝트 구조
```
main
 ┣ static
 ┃ ┣ css
 ┃ ┣ images
 ┃ ┣ js
 ┣ templates
 ┣ application.py  
 ┣ config.py  
 ┣ connection.py   
 ┣ forms.py
 ┣ house_update.py
 ┣ init.py
 ┣ mail.py
 ┣ models.py
 ┣ requirements.txt
 ┗ token_manager.py
```

## 주요 기능
#### 로그인 및 회원가입
* /login
    * 유저가 이메일, 비밀번호를 입력해 로그인을 함
* /register
    * 유저가 프로필 이미지 (선택), 이메일, 비밀번호, 닉네임을 입력하면 입력한 이메일로 인증 메일이 발송됨
* /verify/<token>
    * 유저 이메일을 인증하고 회원가입을 진행해 DB에 /register에서 입력한 정보를 저장
* /logout
    * 로그아웃을 함

#### 게시판 기능
* /board
    * DB에 있는 게시판 글들(자유게시판, 거래게시판) 가져옴
* /free/post
    * 자유게시판 글 작성시 DB에 저장
* /contract/post
    * 거래게시판 글 작성시 DB에 저장
* /move/<<string:topic>>
    * 게시판 글 작성 page로 이동

#### 부동산 기능
* /house
    * 율전동, 천천동에 존재하는 매물들을 크롤링한 DB에서 전체 매물을 가져와 지도에 마커로 표시함(/house/init 호출)
* /house/<<bigint:house_id>>
    * 마커에 표시된 자세히보기를 누를 경우 호출되는 매물 세부정보 페이지
* /house/filters
    * 지도 밑의 필터링 기능
* /house/update
    * 크롤링하여 DB에 매물 정보 업데이트

## 시작하기

### URL
http://swe2023team2-env.eba-bpshwsem.ap-northeast-2.elasticbeanstalk.com/

### Clone Repository (in Local)
```
$ git clone https://github.com/Kangsan419/SWE_Team2.git
$ cd main
```

### Run
config.py를 생성 후 아래 코드를 실행
``` 
# config.py

# Mail 설정
MAIL_SENDER = 'your_email_address'
MAIL_PASSWORD = 'your_password'

# DB 설정
DATABASE_URI = 'your_database'

# AWS S3 설정
BUCKET_NAME = "your_s3_buket_name"
AWS_ACCESS_KEY = "your_access_key"
AWS_SECRET_KEY = "your_secret_key"
```

```
$ python application.py
```

