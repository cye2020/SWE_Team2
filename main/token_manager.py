#사용자 정보 암호화

import secrets
import hashlib
import time


class TokenManager:
    def __init__(self):
        self.tokens = {}

    def generate_token(self, user, profile_image):
        token = secrets.token_hex(16)
        creation_time = int(time.time())
        expiration_time = 3600  # 1시간 동안 유효
        hashed_token = hashlib.sha256(f'{token}.{creation_time}'.encode()).hexdigest()

        self.tokens[hashed_token] = {
            'creation_time': creation_time,
            'expiration_time': expiration_time,
            'verified': False,
            'user': user,
            'profile_image': profile_image
        }

        return hashed_token

    def verify_token(self, token):
        if token in self.tokens:
            user_token_info = self.tokens[token]
            current_time = int(time.time())

            if (
                not user_token_info['verified'] and
                current_time - user_token_info['creation_time'] <= user_token_info['expiration_time']
            ):
                return True

        return False

    def mark_as_verified(self, token):
        if token in self.tokens:
            self.tokens[token]['verified'] = True

    def remove_expired_tokens(self):
        current_time = int(time.time())
        expired_tokens = [token for token, info in self.tokens.items() if current_time - info['creation_time'] > info['expiration_time']]
        
        for token in expired_tokens:
            del self.tokens[token]


