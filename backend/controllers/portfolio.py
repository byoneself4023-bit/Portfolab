# -*- coding: utf-8 -*-
from flask import request, jsonify
from services import portfolio as portfolio_service
from middleware.auth_utils import require_auth


def create():
    """포트폴리오 생성"""
    user_no, role_no, error = require_auth()
    if error:
        return error
    
    data = request.get_json(silent=True) or {}
    name = data.get('name', '').strip()
    description = data.get('description', '').strip()
    
    if not name:
        return jsonify({
            "success": False,
            "message": "포트폴리오 이름은 필수입니다."
        }), 400
    
    if len(name) > 40:
        return jsonify({
            "success": False,
            "message": "포트폴리오 이름은 40자 이내로 입력해주세요."
        }), 400
    
    result, err = portfolio_service.create_portfolio(user_no, name, description)
    
    if err:
        return jsonify({
            "success": False,
            "message": err
        }), 500
    
    return jsonify({
        "success": True,
        "message": "포트폴리오가 생성되었습니다.",
        "data": result
    }), 201


def get_list():
    """내 포트폴리오 목록"""
    user_no, role_no, error = require_auth()
    if error:
        return error
    
    result, err = portfolio_service.get_user_portfolios(user_no)
    
    if err:
        return jsonify({
            "success": False,
            "message": err
        }), 500
    
    return jsonify({
        "success": True,
        "data": result
    }), 200


def get_detail(portfolio_no):
    """포트폴리오 상세 조회"""
    user_no, role_no, error = require_auth()
    if error:
        return error
    
    result, err = portfolio_service.get_portfolio_detail(portfolio_no, user_no)
    
    if err:
        status = 404 if "존재하지 않는" in err else 403 if "권한" in err else 500
        return jsonify({
            "success": False,
            "message": err
        }), status
    
    return jsonify({
        "success": True,
        "data": result
    }), 200


def update(portfolio_no):
    """포트폴리오 수정"""
    user_no, role_no, error = require_auth()
    if error:
        return error
    
    data = request.get_json(silent=True) or {}
    name = data.get('name', '').strip()
    description = data.get('description', '').strip()
    
    if name and len(name) > 40:
        return jsonify({
            "success": False,
            "message": "포트폴리오 이름은 40자 이내로 입력해주세요."
        }), 400
    
    result, err = portfolio_service.update_portfolio(portfolio_no, user_no, name, description)
    
    if err:
        status = 404 if "존재하지 않는" in err else 403 if "권한" in err else 500
        return jsonify({
            "success": False,
            "message": err
        }), status
    
    return jsonify({
        "success": True,
        "message": "포트폴리오가 수정되었습니다.",
        "data": result
    }), 200


def delete(portfolio_no):
    """포트폴리오 삭제"""
    user_no, role_no, error = require_auth()
    if error:
        return error
    
    success, err = portfolio_service.delete_portfolio(portfolio_no, user_no)
    
    if err:
        status = 404 if "존재하지 않는" in err else 403 if "권한" in err else 500
        return jsonify({
            "success": False,
            "message": err
        }), status
    
    return jsonify({
        "success": True,
        "message": "포트폴리오가 삭제되었습니다."
    }), 200
