#DB class들

from flask_login import UserMixin
from init import db


class Member(UserMixin, db.Model):
    __tablename__ = "member"
    login_id = db.Column(db.String(40),primary_key=True, unique=True, nullable=False)
    password = db.Column(db.String(40), nullable=False)
    nickname = db.Column(db.String(40), nullable=False)
    profile_image = db.Column(db.String(255))
    
    def __repr__(self):
        return f"<User {self.login_id}>"
    
    def get_id(self):
        return self.login_id


class House(db.Model):
    
    house_id = db.Column('house_id', db.BigInteger, primary_key=True, nullable=False, default=0)
    house_type = db.Column('house_type', db.String(50), nullable=False, default='')
    pay_type = db.Column('pay_type', db.String(20), nullable=False, default='')
    lat = db.Column('lat', db.Float, nullable=False, default=0.0)
    lon = db.Column('lon', db.Float, nullable=False, default=0.0)
    feature = db.Column('feature', db.String(255), nullable=True, default=None)
    direction = db.Column('direction', db.String(20), nullable=False, default='')
    floor = db.Column('floor', db.String(10), nullable=True, default=None)
    prc = db.Column('prc', db.Integer, nullable=False, default=0)
    rentprc = db.Column('rentprc', db.Integer, nullable=False, default=0)
    space1 = db.Column('space1', db.Integer, nullable=True, default=None)
    space2 = db.Column('space2', db.Integer, nullable=True, default=None)
    taglist = db.Column('taglist', db.JSON, nullable=False, default={})
    imgurl = db.Column('imgurl', db.String(255), nullable=True, default=None)

class free_post(db.Model):
    __tablename__='free_post'
    seq=db.Column('seq',db.Integer,nullable=False,autoincrement=True,primary_key=True)
    title=db.Column('title',db.VARCHAR(30),nullable=True)
    content=db.Column('content',db.Text,nullable=True)
    create_date=db.Column('create_date',db.VARCHAR(20),nullable=True)
    anon=db.Column('anon',db.Boolean,nullable=False, default=False)
    nickname=db.Column('nickname',db.VARCHAR(20),nullable=True)

class contract_post(db.Model):
    __tablename__='contract_post'
    seq=db.Column('seq',db.Integer,nullable=False,autoincrement=True,primary_key=True)
    title=db.Column('title',db.VARCHAR(30),nullable=True)
    object=db.Column('object',db.VARCHAR(20),nullable=True)
    price=db.Column('price',db.VARCHAR(20),nullable=True)
    content=db.Column('content',db.Text,nullable=True)
    create_date=db.Column('create_date',db.VARCHAR(20),nullable=True)
    anon=db.Column('anon',db.Boolean,nullable=False, default=False)
    nickname=db.Column('nickname',db.VARCHAR(20),nullable=True)