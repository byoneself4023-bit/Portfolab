# -*- coding: utf-8 -*-
from flask import Blueprint
from controllers import simulation as simulation_controller

simulation_bp = Blueprint('simulation', __name__, url_prefix='/simulation')


@simulation_bp.route('/<int:portfolio_no>/preview', methods=['POST'])
def preview(portfolio_no):
    """
    What-if 시뮬레이션 미리보기
    
    Request Body:
    {
        "changes": [
            {"stock_no": 1, "quantity_delta": 100},  # 100주 추가 매수
            {"stock_no": 2, "quantity_delta": -50},  # 50주 매도
            {"symbol": "005930", "quantity": 50, "price": 70000}  # 신규 종목 추가
        ]
    }
    
    Response:
    {
        "before": { 분석 결과 },
        "after": { 시뮬레이션 결과 },
        "diff": { 변화량 }
    }
    """
    return simulation_controller.preview(portfolio_no)
