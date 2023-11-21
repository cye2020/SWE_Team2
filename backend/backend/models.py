from flask_login import UserMixin
from init import db


class Member(UserMixin, db.Model):
    __tablename__ = "member"
    login_id = db.Column(db.String(40),primary_key=True, unique=True, nullable=False)
    password = db.Column(db.String(40), nullable=False)
    nickname = db.Column(db.String(40), nullable=False)
    
    def __repr__(self):
        return f"<User {self.login_id}>"
    
    def get_id(self):
        return self.login_id
