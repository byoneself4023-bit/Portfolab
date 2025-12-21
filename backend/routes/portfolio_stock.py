# -*- coding: utf-8 -*-
from flask import Blueprint
from controllers import portfolio_stock as ps_controller

portfolio_stock_bp = Blueprint('portfolio_stock', __name__, url_prefix='/portfolio')


@portfolio_stock_bp.route('/<int:portfolio_no>/stock', methods=['POST'])
def add_stock(portfolio_no):
    """포트폴리오에 종목 추가"""
    return ps_controller.add_stock(portfolio_no)


@portfolio_stock_bp.route('/<int:portfolio_no>/stock', methods=['GET'])
def get_stocks(portfolio_no):
    """포트폴리오 종목 목록"""
    return ps_controller.get_stocks(portfolio_no)


@portfolio_stock_bp.route('/<int:portfolio_no>/stock/<int:stock_no>', methods=['PUT'])
def update_stock(portfolio_no, stock_no):
    """종목 수량/매수가 수정"""
    return ps_controller.update_stock(portfolio_no, stock_no)


@portfolio_stock_bp.route('/<int:portfolio_no>/stock/<int:stock_no>', methods=['DELETE'])
def remove_stock(portfolio_no, stock_no):
    """포트폴리오에서 종목 삭제"""
    return ps_controller.remove_stock(portfolio_no, stock_no)
