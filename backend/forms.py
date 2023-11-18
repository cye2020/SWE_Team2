from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Email, EqualTo, InputRequired, Length, Regexp
from models import Member
from init import bcrypt


class RegisterForm(FlaskForm):
    email = StringField('이메일', validators=[DataRequired(), Email()])
    password = PasswordField('비밀번호', validators=[DataRequired()])
    confirm_password = PasswordField(
        validators=[
            InputRequired(),
            EqualTo("password", message="Passwords must match !"),
        ]
    )
    nickname = StringField(
        validators=[
            InputRequired(),
            Length(3, 20, message="Please provide a valid name"),
            Regexp(
                "^[ㄱ-ㅎ가-힣A-Za-z][ㄱ-ㅎ가-힣A-Za-z0-9_.]*$",
                0,
                "Nickname must have only letters, " "numbers, dots or underscores",
            ),
        ]
    )
    submit = SubmitField('가입하기')
    
    def validate_email(self, email):
        if Member.query.filter_by(login_id=email.data).first():
            raise ValidationError("Email already registered!")



class LoginForm(FlaskForm):
    email = StringField('이메일', validators=[DataRequired(), Email()])
    password = PasswordField('비밀번호', validators=[DataRequired()])
    submit = SubmitField('로그인')
    
    def validate_email(self, email):
        member = Member.query.filter_by(login_id=email.data).first()
        print(f'Password: {member.password}')
        if member is None:
            raise ValidationError("등록되지 않은 이메일 주소입니다")
        
        if not bcrypt.check_password_hash(member.password, self.password.data):
            raise ValidationError("비밀번호가 일치하지 않습니다.")