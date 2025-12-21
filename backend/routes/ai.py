# -*- coding: utf-8 -*-
from flask import Blueprint
from controllers import ai as ai_controller

ai_bp = Blueprint('ai', __name__, url_prefix='/ai')


@ai_bp.route('/analyze/<int:portfolio_no>', methods=['GET'])
def analyze(portfolio_no):
    """포트폴리오 AI 분석"""
    return ai_controller.analyze_portfolio(portfolio_no)


@ai_bp.route('/rebalance/<int:portfolio_no>', methods=['GET'])
def rebalance(portfolio_no):
    """리밸런싱 제안"""
    return ai_controller.get_rebalancing(portfolio_no)


@ai_bp.route('/explain', methods=['GET'])
def explain():
    """지표 설명"""
    return ai_controller.explain_metrics()