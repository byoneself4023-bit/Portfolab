# -*- coding: utf-8 -*-
from flask import request, jsonify
from services import portfolio_stock as ps_service
from services import portfolio as portfolio_service
from middleware.auth_utils import require_auth


def _check_portfolio_owner(portfolio_no, user_no):
    """포트폴리오 소유자 확인"""
    portfolio, error = portfolio_service.get_portfolio_by_no(portfolio_no)
    if error or not portfolio:
        return False, "존재하지 않는 포트폴리오입니다."
    if portfolio.get('user_no') != user_no:
        return False, "권한이 없습니다."
    return True, None


def add_stock(portfolio_no):
    """포트폴리오에 종목 추가"""
    user_no, role_no, error = require_auth()
    if error:
        return error
    
    is_owner, err = _check_portfolio_owner(portfolio_no, user_no)
    if not is_owner:
        status = 404 if "존재하지 않는" in err else 403
        return jsonify({"success": False, "message": err}), status
    
    data = request.get_json(silent=True) or {}
    stock_no = data.get('stock_no')
    symbol = data.get('symbol')  # stock_no 대신 symbol로도 추가 가능
    quantity = data.get('quantity')
    avg_price = data.get('avg_price')
    
    if not quantity or not avg_price:
        return jsonify({
            "success": False,
            "message": "수량(quantity)과 평균매수가(avg_price)는 필수입니다."
        }), 400
    
    if not stock_no and not symbol:
        return jsonify({
            "success": False,
            "message": "stock_no 또는 symbol이 필요합니다."
        }), 400
    
    result, err = ps_service.add_stock(portfolio_no, stock_no, symbol, quantity, avg_price)
    
    if err:
        return jsonify({"success": False, "message": err}), 400
    
    return jsonify({
        "success": True,
        "message": "종목이 추가되었습니다.",
        "data": result
    }), 201


def get_stocks(portfolio_no):
    """포트폴리오 종목 목록"""
    user_no, role_no, error = require_auth()
    if error:
        return error
    
    is_owner, err = _check_portfolio_owner(portfolio_no, user_no)
    if not is_owner:
        status = 404 if "존재하지 않는" in err else 403
        return jsonify({"success": False, "message": err}), status
    
    result, err = ps_service.get_portfolio_stocks(portfolio_no)
    
    if err:
        return jsonify({"success": False, "message": err}), 500
    
    return jsonify({
        "success": True,
        "data": {
            "portfolio_no": portfolio_no,
            "stocks": result,
            "count": len(result) if result else 0
        }
    }), 200


def update_stock(portfolio_no, stock_no):
    """종목 수량/매수가 수정"""
    user_no, role_no, error = require_auth()
    if error:
        return error
    
    is_owner, err = _check_portfolio_owner(portfolio_no, user_no)
    if not is_owner:
        status = 404 if "존재하지 않는" in err else 403
        return jsonify({"success": False, "message": err}), status
    
    data = request.get_json(silent=True) or {}
    quantity = data.get('quantity')
    avg_price = data.get('avg_price')
    
    result, err = ps_service.update_stock(portfolio_no, stock_no, quantity, avg_price)
    
    if err:
        return jsonify({"success": False, "message": err}), 400
    
    return jsonify({
        "success": True,
        "message": "종목 정보가 수정되었습니다.",
        "data": result
    }), 200


def remove_stock(portfolio_no, stock_no):
    """포트폴리오에서 종목 삭제"""
    user_no, role_no, error = require_auth()
    if error:
        return error
    
    is_owner, err = _check_portfolio_owner(portfolio_no, user_no)
    if not is_owner:
        status = 404 if "존재하지 않는" in err else 403
        return jsonify({"success": False, "message": err}), status
    
    success, err = ps_service.remove_stock(portfolio_no, stock_no)
    
    if err:
        return jsonify({"success": False, "message": err}), 400
    
    return jsonify({
        "success": True,
        "message": "종목이 삭제되었습니다."
    }), 200
