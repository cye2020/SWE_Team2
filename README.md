# SWE_Team2
SKKU Introduction to Software Engineering Team 2 Project "구해봐요 성대에 집"

## 프로젝트 소개
성균관대 학생들을 위한 주거공간 커뮤니티

## 멤버 구성
* Frontend(작성요망)
    * 김강산
    * 인진영
    * 정안승
    * 한재웅

* Backend
    * 강준모: 게시판 기능 backend 구현
    * 문보현: 부동산 기능 backend 구현
    * 조예은: 로그인 및 회원가입 backend 구현
    * 진송찬: document 작성 및 presentation 수행

## 개발 환경
* Html, Css
* JS
* AWS( Mysql )
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
 ┣ forms.py
 ┣ init.py
 ┣ mail.py
 ┣ models.py
 ┣ requirements.txt
 ┗ token_manager.py
```

## 주요 기능
#### 로그인 및 회원가입(작성요망)

#### 게시판 기능
* /board
    * DB에 있는 게시판 글들(자유게시판, 거래게시판) 가져옴
* /free/post
    * 자유게시판 글 작성시 DB에 저장
* /contract/post
    * 거래게시판 글 작성시 DB에 저장
* /move/<<string:topic>>
    * 게시판 글 작성 page로 이동

#### 부동산 기능(작성요망)

## 시작하기

### Clone Repository
```
$ git clone https://github.com/Kangsan419/SWE_Team2.git
$ cd main
```

### Run
```
$ python application.py
```

