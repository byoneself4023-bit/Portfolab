# -*- coding: utf-8 -*-
from flask import Blueprint
from controllers import ai as ai_controller

ai_bp = Blueprint('ai', __name__, url_prefix='/ai')


@ai_bp.route('/<int:portfolio_no>/comment', methods=['POST'])
def get_comment(portfolio_no):
    """
    포트폴리오 AI 분석 코멘트
    
    Claude API를 사용하여 포트폴리오 장단점 분석
    
    Response:
    {
        "comment": "분석 코멘트...",
        "suggestions": ["제안1", "제안2", ...]
    }
    """
    return ai_controller.get_comment(portfolio_no)
