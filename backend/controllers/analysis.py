# -*- coding: utf-8 -*-
from flask import jsonify
from services import analysis as analysis_service
from services import portfolio as portfolio_service
from middleware.auth_utils import require_auth


def _check_portfolio_access(portfolio_no, user_no):
    """포트폴리오 접근 권한 확인"""
    portfolio, error = portfolio_service.get_portfolio_by_no(portfolio_no)
    if error or not portfolio:
        return False, "존재하지 않는 포트폴리오입니다."
    if portfolio.get('user_no') != user_no:
        return False, "권한이 없습니다."
    return True, None


def get_summary(portfolio_no):
    """기본 지표 (수익률, 평가금액)"""
    user_no, role_no, error = require_auth()
    if error:
        return error
    
    has_access, err = _check_portfolio_access(portfolio_no, user_no)
    if not has_access:
        status = 404 if "존재하지 않는" in err else 403
        return jsonify({"success": False, "message": err}), status
    
    result, err = analysis_service.get_portfolio_summary(portfolio_no)
    
    if err:
        return jsonify({"success": False, "message": err}), 500
    
    return jsonify({
        "success": True,
        "data": result
    }), 200


def get_risk(portfolio_no):
    """리스크 지표 (변동성, 샤프비율)"""
    user_no, role_no, error = require_auth()
    if error:
        return error
    
    has_access, err = _check_portfolio_access(portfolio_no, user_no)
    if not has_access:
        status = 404 if "존재하지 않는" in err else 403
        return jsonify({"success": False, "message": err}), status
    
    result, err = analysis_service.get_risk_metrics(portfolio_no)
    
    if err:
        return jsonify({"success": False, "message": err}), 500
    
    return jsonify({
        "success": True,
        "data": result
    }), 200


def get_correlation(portfolio_no):
    """상관관계 매트릭스"""
    user_no, role_no, error = require_auth()
    if error:
        return error
    
    has_access, err = _check_portfolio_access(portfolio_no, user_no)
    if not has_access:
        status = 404 if "존재하지 않는" in err else 403
        return jsonify({"success": False, "message": err}), status
    
    result, err = analysis_service.get_correlation_matrix(portfolio_no)
    
    if err:
        return jsonify({"success": False, "message": err}), 500
    
    return jsonify({
        "success": True,
        "data": result
    }), 200


def get_sector(portfolio_no):
    """섹터 분포"""
    user_no, role_no, error = require_auth()
    if error:
        return error
    
    has_access, err = _check_portfolio_access(portfolio_no, user_no)
    if not has_access:
        status = 404 if "존재하지 않는" in err else 403
        return jsonify({"success": False, "message": err}), status
    
    result, err = analysis_service.get_sector_distribution(portfolio_no)
    
    if err:
        return jsonify({"success": False, "message": err}), 500
    
    return jsonify({
        "success": True,
        "data": result
    }), 200
