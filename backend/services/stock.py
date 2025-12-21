# -*- coding: utf-8 -*-
from model import stock as stock_model
from utils.external_api import kis_api


def search_stock(query, market=None):
    """종목 검색 (DB에서 검색)"""
    try:
        results = stock_model.search_by_name_or_symbol(query, market)
        return results, None
    except Exception as e:
        return None, str(e)


def get_stock_detail(symbol):
    """종목 상세 조회"""
    try:
        stock = stock_model.find_by_symbol(symbol)
        if not stock:
            return None, "존재하지 않는 종목입니다."
        return stock, None
    except Exception as e:
        return None, str(e)


def get_price_history(symbol, days=90):
    """가격 히스토리 조회"""
    try:
        stock = stock_model.find_by_symbol(symbol)
        if not stock:
            return None, "존재하지 않는 종목입니다."
        
        history = stock_model.get_price_history(stock['stock_no'], days)
        return {
            "symbol": symbol,
            "name": stock['name'],
            "history": history
        }, None
    except Exception as e:
        return None, str(e)


def get_current_price(symbol):
    """현재가 조회 (한투 API)"""
    try:
        price_data = kis_api.get_stock_price(symbol)
        if not price_data:
            return None, "시세 조회에 실패했습니다."
        
        # DB에 현재가 업데이트
        stock_model.update_current_price(symbol, price_data['current_price'])
        
        return price_data, None
    except Exception as e:
        return None, str(e)


def get_or_create_stock(symbol):
    """종목 조회 또는 생성 (한투 API로 정보 가져오기)"""
    stock = stock_model.find_by_symbol(symbol)
    if stock:
        return stock, None
    
    # 한투 API에서 종목 정보 조회
    try:
        stock_info = kis_api.get_stock_info(symbol)
        if not stock_info:
            return None, "종목 정보를 찾을 수 없습니다."
        
        stock_no = stock_model.create_stock(stock_info)
        stock_info['stock_no'] = stock_no
        return stock_info, None
    except Exception as e:
        return None, str(e)

def get_stock_list():
    """전체 종목 목록 조회"""
    try:
        results = stock_model.get_all_stocks()
        return results, None
    except Exception as e:
        return None, str(e)

def update_all_prices():
    """전체 종목 현재가 일괄 업데이트"""
    try:
        stocks = stock_model.get_all_stocks()
        updated = 0
        failed = 0
        
        for stock in stocks:
            try:
                price_data = kis_api.get_stock_price(stock['symbol'])
                if price_data:
                    stock_model.update_current_price(stock['symbol'], price_data['current_price'])
                    updated += 1
                else:
                    failed += 1
            except:
                failed += 1
        
        return {"updated": updated, "failed": failed}, None
    except Exception as e:
        return None, str(e)

def update_price_history(symbol, days=90):
    """종목 가격 히스토리 업데이트"""
    try:
        stock = stock_model.find_by_symbol(symbol)
        if not stock:
            return None, "종목을 찾을 수 없습니다."
        
        history = kis_api.get_price_history(symbol, period="D", count=days)
        if not history:
            return None, "히스토리 조회 실패"
        
        # DB에 저장
        for h in history:
            stock_model.insert_price_history(
                stock['stock_no'],
                h['date'],
                h['open_price'],
                h['high_price'],
                h['low_price'],
                h['close_price'],
                h['volume']
            )
        
        return {"symbol": symbol, "count": len(history)}, None
    except Exception as e:
        return None, str(e)


def update_all_price_history():
    """전체 종목 가격 히스토리 업데이트"""
    try:
        stocks = stock_model.get_all_stocks()
        updated = 0
        failed = 0
        
        for stock in stocks:
            result, error = update_price_history(stock['symbol'])
            if result:
                updated += 1
            else:
                failed += 1
        
        return {"updated": updated, "failed": failed}, None
    except Exception as e:
        return None, str(e)