import secrets
import hashlib
import time
from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, email: str, password: str = None, nickname: str = None):
        self.email = email
        self.password = password
        self.nickname = nickname
    
    def get_id(self):
        return self.email

    def __repr__(self):
        return f"USER: {self.email} = {self.nickname}"
    
    # DB와 연결해서 이미 존재하는 아이디인지 확인
    def check_registered(self):
        return False
    
    # DB와 연결해서 유저를 등록
    def register(self):
        pass
    
    # DB와 연결해서 login 가능한지 확인
    def login(self):
        # if self.email and self.password:
        #     self.nickname = ''
        #     return True
        # else:
        #     return False
        return True

    # 로그 아웃
    def logout():
        pass
    
    # 회원 탈퇴
    def unregister():
        pass


class Profile():
    def __init__(user_id: str):
        pass
    
    def generate():
        pass
    
    def delete():
        pass
    
    def modify():
        pass



class TokenManager:
    def __init__(self):
        self.tokens = {}

    def generate_token(self, user_email, password, nickname):
        token = secrets.token_hex(16)
        creation_time = int(time.time())
        expiration_time = 3600  # 1시간 동안 유효
        hashed_token = hashlib.sha256(f'{token}.{creation_time}'.encode()).hexdigest()

        self.tokens[user_email] = {
            'token': hashed_token,
            'creation_time': creation_time,
            'expiration_time': expiration_time,
            'verified': False,
            'user_info': {
                'password': password,
                'nickname': nickname
            }
        }

        return hashed_token

    def verify_token(self, user_email, token):
        if user_email in self.tokens:
            user_token_info = self.tokens[user_email]
            current_time = int(time.time())

            if (
                not user_token_info['verified'] and
                current_time - user_token_info['creation_time'] <= user_token_info['expiration_time']
            ):
                return user_token_info['token'] == token

        return False

    def mark_as_verified(self, user_email):
        if user_email in self.tokens:
            self.tokens[user_email]['verified'] = True

    def remove_expired_tokens(self):
        current_time = int(time.time())
        expired_tokens = [email for email, info in self.tokens.items() if current_time - info['creation_time'] > info['expiration_time']]
        
        for email in expired_tokens:
            del self.tokens[email]