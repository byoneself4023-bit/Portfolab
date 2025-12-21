# -*- coding: utf-8 -*-
import bcrypt
import jwt
import os
import re
from datetime import datetime, timedelta
from model import user as user_model


def validate_email(email):
    """이메일 형식 검증"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password):
    """
    비밀번호 정책 검증
    - 6~30자
    - 영문, 숫자, 특수문자 중 2가지 이상 조합
    """
    if len(password) < 6 or len(password) > 30:
        return False, "비밀번호는 6~30자 이내로 입력해주세요."
    
    has_letter = bool(re.search(r'[a-zA-Z]', password))
    has_digit = bool(re.search(r'\d', password))
    has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
    
    count = sum([has_letter, has_digit, has_special])
    if count < 2:
        return False, "비밀번호는 영문, 숫자, 특수문자 중 2가지 이상을 포함해야 합니다."
    
    return True, None


def hash_password(password):
    """비밀번호 해싱"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(password, hashed):
    """비밀번호 검증"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


def generate_token(user_no, role_no):
    """JWT 토큰 생성"""
    secret_key = os.getenv('JWT_SECRET_KEY', 'default-secret-key')
    payload = {
        'user_no': user_no,
        'role_no': role_no,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, secret_key, algorithm='HS256')


def register(email, password, nickname):
    """회원가입"""
    # 이메일 형식 검증
    if not validate_email(email):
        return None, "올바른 이메일 형식이 아닙니다."
    
    # 비밀번호 정책 검증
    is_valid, error = validate_password(password)
    if not is_valid:
        return None, error
    
    # 이메일 중복 확인
    existing = user_model.find_by_email(email)
    if existing:
        return None, "이미 사용 중인 이메일입니다."
    
    # 비밀번호 해싱
    hashed_password = hash_password(password)
    
    # 사용자 생성
    user_no = user_model.create_user(email, hashed_password, nickname)
    
    if not user_no:
        return None, "회원가입 처리 중 오류가 발생했습니다."
    
    return {
        "user_no": user_no,
        "email": email,
        "nickname": nickname
    }, None


def login(email, password):
    """로그인"""
    user = user_model.find_by_email(email)
    
    if not user:
        return None, "이메일 또는 비밀번호가 일치하지 않습니다."
    
    if user.get('is_deleted'):
        return None, "탈퇴한 계정입니다."
    
    if not verify_password(password, user['password']):
        return None, "이메일 또는 비밀번호가 일치하지 않습니다."
    
    token = generate_token(user['user_no'], user['role_no'])
    
    return {
        "token": token,
        "user_no": user['user_no'],
        "nickname": user['nickname'],
        "role_no": user['role_no']
    }, None


def get_user_info(user_no):
    """사용자 정보 조회"""
    user = user_model.find_by_no(user_no)
    
    if not user:
        return None, "사용자를 찾을 수 없습니다."
    
    return {
        "user_no": user['user_no'],
        "email": user['email'],
        "nickname": user['nickname'],
        "role_no": user['role_no']
    }, None
