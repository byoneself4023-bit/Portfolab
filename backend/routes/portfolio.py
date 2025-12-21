# -*- coding: utf-8 -*-
from flask import Blueprint
from controllers import portfolio as portfolio_controller

portfolio_bp = Blueprint('portfolio', __name__, url_prefix='/portfolio')


@portfolio_bp.route('', methods=['POST'])
def create():
    """포트폴리오 생성"""
    return portfolio_controller.create()


@portfolio_bp.route('', methods=['GET'])
def get_list():
    """내 포트폴리오 목록"""
    return portfolio_controller.get_list()


@portfolio_bp.route('/<int:portfolio_no>', methods=['GET'])
def get_detail(portfolio_no):
    """포트폴리오 상세 조회"""
    return portfolio_controller.get_detail(portfolio_no)


@portfolio_bp.route('/<int:portfolio_no>', methods=['PUT'])
def update(portfolio_no):
    """포트폴리오 수정"""
    return portfolio_controller.update(portfolio_no)


@portfolio_bp.route('/<int:portfolio_no>', methods=['DELETE'])
def delete(portfolio_no):
    """포트폴리오 삭제"""
    return portfolio_controller.delete(portfolio_no)
