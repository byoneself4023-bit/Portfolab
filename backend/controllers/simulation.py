# -*- coding: utf-8 -*-
from flask import request, jsonify
from services import simulation as simulation_service
from services import portfolio as portfolio_service
from middleware.auth_utils import require_auth


def preview(portfolio_no):
    """What-if 시뮬레이션 미리보기"""
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
    
    data = request.get_json(silent=True) or {}
    changes = data.get('changes', [])
    
    if not changes:
        return jsonify({
            "success": False,
            "message": "변경사항(changes)을 입력해주세요."
        }), 400
    
    result, err = simulation_service.simulate_changes(portfolio_no, changes)
    
    if err:
        return jsonify({
            "success": False,
            "message": err
        }), 500
    
    return jsonify({
        "success": True,
        "data": result
    }), 200
