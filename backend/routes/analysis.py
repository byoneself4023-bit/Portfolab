# -*- coding: utf-8 -*-
from flask import Blueprint
from controllers import analysis as analysis_controller

analysis_bp = Blueprint('analysis', __name__, url_prefix='/analysis')


@analysis_bp.route('/<int:portfolio_no>/summary', methods=['GET'])
def get_summary(portfolio_no):
    """기본 지표 (수익률, 평가금액)"""
    return analysis_controller.get_summary(portfolio_no)


@analysis_bp.route('/<int:portfolio_no>/risk', methods=['GET'])
def get_risk(portfolio_no):
    """리스크 지표 (변동성, 샤프비율, 베타)"""
    return analysis_controller.get_risk(portfolio_no)


@analysis_bp.route('/<int:portfolio_no>/correlation', methods=['GET'])
def get_correlation(portfolio_no):
    """상관관계 매트릭스"""
    return analysis_controller.get_correlation(portfolio_no)


@analysis_bp.route('/<int:portfolio_no>/sector', methods=['GET'])
def get_sector(portfolio_no):
    """섹터 분포"""
    return analysis_controller.get_sector(portfolio_no)
