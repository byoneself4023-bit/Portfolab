# -*- coding: utf-8 -*-
from flask import jsonify
from services import ai as ai_service
from services import portfolio as portfolio_service
from middleware.auth_utils import require_auth


def get_comment(portfolio_no):
    """포트폴리오 AI 분석 코멘트"""
    user_no, role_no, error = require_auth()
    if error:
        return error
    
    # 포트폴리오 접근 권한 확인
    portfolio, err = portfolio_service.get_portfolio_by_no(portfolio_no)
    if err or not portfolio:
        return jsonify({
            "success": False,
            "message": "존재하지 않는 포트폴리오입니다."
        }), 404
    
    if portfolio.get('user_no') != user_no:
        return jsonify({
            "success": False,
            "message": "권한이 없습니다."
        }), 403
    
    result, err = ai_service.get_portfolio_comment(portfolio_no)
    
    if err:
        return jsonify({
            "success": False,
            "message": err
        }), 500
    
    return jsonify({
        "success": True,
        "data": result
    }), 200
