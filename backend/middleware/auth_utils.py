# -*- coding: utf-8 -*-
from flask import request, jsonify
from functools import wraps
import jwt
import os


def get_token_from_header():
    """Authorization 헤더에서 토큰 추출"""
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None
    
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != 'bearer':
        return None
    
    return parts[1]


def decode_token(token):
    """JWT 토큰 디코딩"""
    try:
        secret_key = os.getenv('JWT_SECRET_KEY', 'default-secret-key')
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        return payload, None
    except jwt.ExpiredSignatureError:
        return None, "토큰이 만료되었습니다."
    except jwt.InvalidTokenError:
        return None, "유효하지 않은 토큰입니다."


def require_auth():
    """
    인증 필요한 엔드포인트에서 호출
    반환: (user_no, role_no, error_response)
    - 성공: (user_no, role_no, None)
    - 실패: (None, None, jsonify_error_response)
    """
    token = get_token_from_header()
    if not token:
        return None, None, (jsonify({
            "success": False,
            "message": "인증 토큰이 필요합니다."
        }), 401)
    
    payload, error = decode_token(token)
    if error:
        return None, None, (jsonify({
            "success": False,
            "message": error
        }), 401)
    
    user_no = payload.get('user_no')
    role_no = payload.get('role_no', 1)
    
    return user_no, role_no, None


def require_admin():
    """
    관리자 권한 필요한 엔드포인트에서 호출
    """
    user_no, role_no, error = require_auth()
    if error:
        return None, None, error
    
    if role_no != 2:  # 2 = ADMIN
        return None, None, (jsonify({
            "success": False,
            "message": "관리자 권한이 필요합니다."
        }), 403)
    
    return user_no, role_no, None


def token_required(f):
    """데코레이터 버전 인증 체크"""
    @wraps(f)
    def decorated(*args, **kwargs):
        user_no, role_no, error = require_auth()
        if error:
            return error
        return f(user_no=user_no, role_no=role_no, *args, **kwargs)
    return decorated
