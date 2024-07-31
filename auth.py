from .models import find_user_by_email

def verify_password(plain_password, stored_password) -> bool:
    return plain_password == stored_password

def authenticate_user(email: str, password: str):
    user = find_user_by_email(email)
    if not user or not verify_password(password, user['password']):
        return False
    return user
