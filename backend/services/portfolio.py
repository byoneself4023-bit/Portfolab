# -*- coding: utf-8 -*-
from model import portfolio as portfolio_model
from model import portfolio_stock as ps_model


def create_portfolio(user_no, name, description=''):
    """포트폴리오 생성"""
    try:
        portfolio_no = portfolio_model.create(user_no, name, description)
        if not portfolio_no:
            return None, "포트폴리오 생성에 실패했습니다."
        
        return {
            "portfolio_no": portfolio_no,
            "name": name,
            "description": description
        }, None
    except Exception as e:
        return None, str(e)


def get_user_portfolios(user_no):
    """사용자의 포트폴리오 목록"""
    try:
        portfolios = portfolio_model.find_by_user_no(user_no)
        
        # 각 포트폴리오의 종목 수와 평가금액 추가
        for p in portfolios:
            stocks = ps_model.find_by_portfolio_no(p['portfolio_no'])
            p['stock_count'] = len(stocks) if stocks else 0
            # TODO: 평가금액 계산 추가
        
        return portfolios, None
    except Exception as e:
        return None, str(e)


def get_portfolio_by_no(portfolio_no):
    """포트폴리오 조회 (소유자 확인용)"""
    try:
        portfolio = portfolio_model.find_by_no(portfolio_no)
        return portfolio, None
    except Exception as e:
        return None, str(e)


def get_portfolio_detail(portfolio_no, user_no):
    """포트폴리오 상세 조회"""
    try:
        portfolio = portfolio_model.find_by_no(portfolio_no)
        
        if not portfolio:
            return None, "존재하지 않는 포트폴리오입니다."
        
        if portfolio['user_no'] != user_no:
            return None, "권한이 없습니다."
        
        # 종목 목록 포함
        stocks = ps_model.find_by_portfolio_no_with_stock_info(portfolio_no)
        portfolio['stocks'] = stocks if stocks else []
        portfolio['stock_count'] = len(portfolio['stocks'])
        
        return portfolio, None
    except Exception as e:
        return None, str(e)


def update_portfolio(portfolio_no, user_no, name=None, description=None):
    """포트폴리오 수정"""
    try:
        portfolio = portfolio_model.find_by_no(portfolio_no)
        
        if not portfolio:
            return None, "존재하지 않는 포트폴리오입니다."
        
        if portfolio['user_no'] != user_no:
            return None, "권한이 없습니다."
        
        # 변경할 값만 업데이트
        update_data = {}
        if name:
            update_data['name'] = name
        if description is not None:
            update_data['description'] = description
        
        if update_data:
            success = portfolio_model.update(portfolio_no, update_data)
            if not success:
                return None, "수정에 실패했습니다."
        
        # 수정된 정보 반환
        updated = portfolio_model.find_by_no(portfolio_no)
        return updated, None
    except Exception as e:
        return None, str(e)


def delete_portfolio(portfolio_no, user_no):
    """포트폴리오 삭제"""
    try:
        portfolio = portfolio_model.find_by_no(portfolio_no)
        
        if not portfolio:
            return False, "존재하지 않는 포트폴리오입니다."
        
        if portfolio['user_no'] != user_no:
            return False, "권한이 없습니다."
        
        success = portfolio_model.delete(portfolio_no)
        return success, None if success else "삭제에 실패했습니다."
    except Exception as e:
        return False, str(e)
