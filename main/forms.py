#로그인 및 회원가입 처리

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, ValidationError
from flask_wtf.file import FileAllowed, FileField
from wtforms.validators import DataRequired, Email, EqualTo, InputRequired, Length, Regexp
from models import Member
from init import bcrypt


class RegisterForm(FlaskForm):
    email = StringField('이메일', validators=[
        DataRequired(),
        Regexp(r'^[a-zA-Z0-9._%+-]+$', message='유효한 이메일 주소를 입력하세요')
    ])
    password = PasswordField('비밀번호', validators=[DataRequired()])
    confirm_password = PasswordField(
        validators=[
            InputRequired(),
            EqualTo("password", message="비밀번호가 일치하지 않습니다."),
        ]
    )
    nickname = StringField(
        validators=[
            InputRequired(),
            Length(3, 20, message="닉네임은 3글자 이상, 20글자 이하로 입력해주세요."),
            Regexp(
                "^[ㄱ-ㅎ가-힣A-Za-z][ㄱ-ㅎ가-힣A-Za-z0-9_.]*$",
                0,
                "닉네임은 한글, 영어, 숫자, '.', '_'만 사용할 수 있습니다. ",
            ),
        ]
    )
    profile_image = FileField('프로필 이미지', validators=[FileAllowed(['jpg', 'png'], '이미지 파일만 업로드 가능합니다.')])
    submit = SubmitField('가입하기')
    
    def validate_email(self, email):
        if Member.query.filter_by(login_id=(email.data + "@g.skku.edu")).first():
            raise ValidationError("이미 등록된 이메일입니다!")



class LoginForm(FlaskForm):
    email = StringField('ID', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('로그인')
    
    def validate_email(self, email):
        member = Member.query.filter_by(login_id=email.data).first()
        
        if member is None:
            raise ValidationError("등록되지 않은 이메일 주소입니다")
    
    def validate_password(self, password):
        member = Member.query.filter_by(login_id=self.email.data).first()
        
        if member is not None:
            if not bcrypt.check_password_hash(member.password, self.password.data):
                raise ValidationError("비밀번호가 일치하지 않습니다.")