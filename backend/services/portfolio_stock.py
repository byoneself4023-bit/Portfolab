# -*- coding: utf-8 -*-
from model import portfolio_stock as ps_model
from model import stock as stock_model
from services import stock as stock_service


def add_stock(portfolio_no, stock_no=None, symbol=None, quantity=None, avg_price=None):
    """포트폴리오에 종목 추가"""
    try:
        # symbol로 요청한 경우 stock_no 조회/생성
        if not stock_no and symbol:
            stock, error = stock_service.get_or_create_stock(symbol)
            if error:
                return None, error
            stock_no = stock['stock_no']
        
        # 이미 존재하는지 확인
        if ps_model.exists(portfolio_no, stock_no):
            return None, "이미 포트폴리오에 추가된 종목입니다."
        
        # 추가
        success = ps_model.insert(portfolio_no, stock_no, quantity, avg_price)
        if not success:
            return None, "종목 추가에 실패했습니다."
        
        # 추가된 종목 정보 반환
        stock = stock_model.find_by_no(stock_no)
        return {
            "portfolio_no": portfolio_no,
            "stock_no": stock_no,
            "symbol": stock['symbol'] if stock else None,
            "name": stock['name'] if stock else None,
            "quantity": quantity,
            "avg_price": avg_price
        }, None
    except Exception as e:
        return None, str(e)


def get_portfolio_stocks(portfolio_no):
    """포트폴리오 종목 목록"""
    try:
        stocks = ps_model.find_by_portfolio_no_with_stock_info(portfolio_no)
        return stocks if stocks else [], None
    except Exception as e:
        return None, str(e)


def update_stock(portfolio_no, stock_no, quantity=None, avg_price=None):
    """종목 수량/매수가 수정"""
    try:
        if not ps_model.exists(portfolio_no, stock_no):
            return None, "포트폴리오에 해당 종목이 없습니다."
        
        update_data = {}
        if quantity is not None:
            update_data['quantity'] = quantity
        if avg_price is not None:
            update_data['avg_price'] = avg_price
        
        if not update_data:
            return None, "수정할 내용이 없습니다."
        
        success = ps_model.update(portfolio_no, stock_no, update_data)
        if not success:
            return None, "수정에 실패했습니다."
        
        # 수정된 정보 반환
        stock_info = ps_model.find_one(portfolio_no, stock_no)
        return stock_info, None
    except Exception as e:
        return None, str(e)


def remove_stock(portfolio_no, stock_no):
    """포트폴리오에서 종목 삭제"""
    try:
        if not ps_model.exists(portfolio_no, stock_no):
            return False, "포트폴리오에 해당 종목이 없습니다."
        
        success = ps_model.delete(portfolio_no, stock_no)
        return success, None if success else "삭제에 실패했습니다."
    except Exception as e:
        return False, str(e)
