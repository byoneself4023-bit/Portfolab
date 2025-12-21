# -*- coding: utf-8 -*-
from flask import Blueprint
from controllers import stock as stock_controller

stock_bp = Blueprint('stock', __name__, url_prefix='/stock')


@stock_bp.route('/search', methods=['GET'])
def search():
    """종목 검색"""
    return stock_controller.search()


@stock_bp.route('/<string:symbol>', methods=['GET'])
def get_stock(symbol):
    """종목 상세 조회"""
    return stock_controller.get_stock(symbol)


@stock_bp.route('/<string:symbol>/history', methods=['GET'])
def get_history(symbol):
    """가격 히스토리 조회"""
    return stock_controller.get_history(symbol)


@stock_bp.route('/price/<string:symbol>', methods=['GET'])
def get_current_price(symbol):
    """현재가 조회 (한투 API)"""
    return stock_controller.get_current_price(symbol)

@stock_bp.route('/list', methods=['GET'])
def get_list():
    """전체 종목 목록 조회"""
    return stock_controller.get_list()

@stock_bp.route('/update-prices', methods=['POST'])
def update_all_prices():
    """전체 종목 현재가 일괄 업데이트"""
    return stock_controller.update_all_prices()
