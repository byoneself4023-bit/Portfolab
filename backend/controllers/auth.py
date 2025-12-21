# -*- coding: utf-8 -*-
from flask import request, jsonify
from services import auth as auth_service
from middleware.auth_utils import require_auth


def register():
    """회원가입"""
    data = request.get_json(silent=True) or {}
    
    email = data.get('email', '').strip()
    password = data.get('password', '')
    nickname = data.get('nickname', '').strip()
    
    # 입력값 검증
    if not email or not password or not nickname:
        return jsonify({
            "success": False,
            "message": "이메일, 비밀번호, 닉네임은 필수입니다."
        }), 400
    
    result, error = auth_service.register(email, password, nickname)
    
    if error:
        return jsonify({
            "success": False,
            "message": error
        }), 400
    
    return jsonify({
        "success": True,
        "message": "회원가입이 완료되었습니다.",
        "data": result
    }), 201


def login():
    """로그인"""
    data = request.get_json(silent=True) or {}
    
    email = data.get('email', '').strip()
    password = data.get('password', '')
    
    if not email or not password:
        return jsonify({
            "success": False,
            "message": "이메일과 비밀번호를 입력해주세요."
        }), 400
    
    result, error = auth_service.login(email, password)
    
    if error:
        return jsonify({
            "success": False,
            "message": error
        }), 401
    
    return jsonify({
        "success": True,
        "message": "로그인 성공",
        "data": result
    }), 200


def verify():
    """토큰 검증"""
    user_no, role_no, error = require_auth()
    
    if error:
        return error
    
    result, err = auth_service.get_user_info(user_no)
    
    if err:
        return jsonify({
            "success": False,
            "message": err
        }), 404
    
    return jsonify({
        "success": True,
        "data": result
    }), 200
