from fastapi_login import LoginManager
from passlib.context import CryptContext
import os

SECRET = os.environ['SECRET']
manager = LoginManager(SECRET, token_url='/token', use_cookie=True)
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)