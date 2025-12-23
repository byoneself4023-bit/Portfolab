# -*- coding: utf-8 -*-
from flask import request, jsonify
from services import simulation as simulation_service
from services import portfolio as portfolio_service
from services.optimizer import markowitz_optimize          # 추가
from services.monte_carlo import run_simulation as mc_simulation  # 추가
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

def optimize(portfolio_no):
    """마코위츠 최적화"""
    # 테스트용: 인증 임시 제거
    try:
        result = markowitz_optimize(portfolio_no)
        if "error" in result:
            return jsonify({"success": False, "message": result["error"]}), 400
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


def monte_carlo(portfolio_no):
    """몬테카를로 시뮬레이션"""
    # 테스트용: 인증 임시 제거
    try:
        years = request.args.get('years', 10, type=int)
        simulations = request.args.get('simulations', 1000, type=int)
        
        result = mc_simulation(portfolio_no, years, simulations)
        if "error" in result:
            return jsonify({"success": False, "message": result["error"]}), 400
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500