# -*- coding: utf-8 -*-
from flask import request, jsonify
from services import stock as stock_service


def search():
    """종목 검색"""
    query = request.args.get('q', '').strip()
    market = request.args.get('market', '')  # KOSPI, KOSDAQ, ETF
    
    if not query:
        return jsonify({
            "success": False,
            "message": "검색어를 입력해주세요."
        }), 400
    
    results, error = stock_service.search_stock(query, market)
    
    if error:
        return jsonify({
            "success": False,
            "message": error
        }), 500
    
    return jsonify({
        "success": True,
        "data": results
    }), 200


def get_stock(symbol):
    """종목 상세 조회"""
    result, error = stock_service.get_stock_detail(symbol)
    
    if error:
        return jsonify({
            "success": False,
            "message": error
        }), 404
    
    return jsonify({
        "success": True,
        "data": result
    }), 200


def get_history(symbol):
    """가격 히스토리 조회"""
    days = request.args.get('days', 90, type=int)
    
    result, error = stock_service.get_price_history(symbol, days)
    
    if error:
        return jsonify({
            "success": False,
            "message": error
        }), 404
    
    return jsonify({
        "success": True,
        "data": result
    }), 200


def get_current_price(symbol):
    """현재가 조회 (한투 API)"""
    result, error = stock_service.get_current_price(symbol)
    
    if error:
        return jsonify({
            "success": False,
            "message": error
        }), 500
    
    return jsonify({
        "success": True,
        "data": result
    }), 200


def get_list():
    """전체 종목 목록 조회"""
    result, error = stock_service.get_stock_list()
    
    if error:
        return jsonify({
            "success": False,
            "message": error
        }), 500
    
    return jsonify({
        "success": True,
        "data": result
    }), 200


def update_all_prices():
    """전체 종목 현재가 일괄 업데이트"""
    result, error = stock_service.update_all_prices()
    
    if error:
        return jsonify({
            "success": False,
            "message": error
        }), 500
    
    return jsonify({
        "success": True,
        "message": f"{result['updated']}개 종목 업데이트 완료",
        "data": result
    }), 200