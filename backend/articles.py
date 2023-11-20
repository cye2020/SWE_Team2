from flask import Flask, render_template,request,redirect,url_for,jsonify
from flask_sqlalchemy import SQLAlchemy

app=Flask(__name__)

#DB 정보
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:peter0107@database-1.cc0lokhfxaeb.us-east-2.rds.amazonaws.com/software_database'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db=SQLAlchemy(app)

class free_post(db.Model):
    __tablename__='free_post'
    seq=db.Column('seq',db.Integer,nullable=False,autoincrement=True,primary_key=True)
    title=db.Column('title',db.VARCHAR(30),nullable=True)
    content=db.Column('content',db.Text,nullable=True)
    writer_id=db.Column('writer_id',db.VARCHAR(30),nullable=True)
    create_date=db.Column('create_date',db.VARCHAR(20),nullable=True)
    anon=db.Column('anon',db.Boolean,nullable=False, default=False)
    

#게시물 등록창(최신 네개의 게시물을 가져옴)
@app.route('/')
def hello():
    try:

        post = free_post.query.order_by(free_post.create_date.desc()).first()
        post_data = {
            'title': post.title,
            'content': post.content,
            'writer_id': post.writer_id,
            'create_date': post.create_date
        }

        return render_template("bulletin.html",post=post_data)
    except:
        return render_template


    

#게시물 작성하러가기(완료)
@app.route('/free/move', methods=['GET'])
def move():
    return render_template('notification.html')


#GET 최신 네 개의 게시물을 가져옴
@app.route('/free',methods=['GET'])
def board():
    post=free_post.query.limit(1).all()

    return render_template('articles.html',post=post)

#GET 모든 게시물을 가져옴
@app.route('/free/articles', methods=['GET'])
def articles():
    posts=free_post.query.all()

    return render_template('articles.html',posts=posts)


#GET seq에 해당하는 게시글 정보와 댓글을 가져옴
@app.route('/free/select/<int:num>',methods=['GET'])
def select(num):
    selected_post=free_post.query.filter_by(seq=num).all()
    if selected_post:
        return render_template('articles.html', posts=selected_post)
    else:
        return "Post not found"

#POST 게시물 DB(post)에 저장(완료)
@app.route('/free/post', methods=['POST'])
def post():
    #title과 content 가져오기
    title=request.form.get('title')
    anon_status=request.form.get('anon')
    content=request.form.get('content')
    writer_id="peterjm007@naver.com"
    create_date=request.form.get('timestamp')
    
    #익명여부
    if anon_status=='none':
        anon=False
    else:
        anon=True
    

    #DB에 저장할 board_post 객체 생성
    new_post=free_post(title=title,content=content, anon=anon,writer_id=writer_id,create_date=create_date)
    
    db.session.add(new_post)
    db.session.commit()
    return "Post successfully added to the database"
   
    

#POST 댓글 DB(comment)에 저장
@app.route('/free/comment')
def comment():
    return "hello"

if __name__=='__main__':
    app.run(debug=True)