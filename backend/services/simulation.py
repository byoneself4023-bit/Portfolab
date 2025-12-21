# -*- coding: utf-8 -*-
from model import portfolio_stock as ps_model
from model import stock as stock_model
from services import analysis as analysis_service
from services import stock as stock_service


def simulate_changes(portfolio_no, changes):
    """
    What-if 시뮬레이션
    
    changes 형식:
    [
        {"stock_no": 1, "quantity_delta": 100},    # 기존 종목 수량 변경
        {"stock_no": 2, "quantity_delta": -50},   # 기존 종목 매도
        {"symbol": "005930", "quantity": 50, "price": 70000}  # 신규 종목 추가
    ]
    """
    try:
        # 1. 현재 포트폴리오 분석 결과 (before)
        before_summary, err = analysis_service.get_portfolio_summary(portfolio_no)
        if err:
            return None, err
        
        before_risk, err = analysis_service.get_risk_metrics(portfolio_no)
        if err:
            return None, err
        
        # 2. 가상 포트폴리오 생성 (현재 종목 복사)
        current_stocks = ps_model.find_by_portfolio_no_with_stock_info(portfolio_no)
        simulated_stocks = {s['stock_no']: dict(s) for s in current_stocks}
        
        # 3. 변경사항 적용
        for change in changes:
            stock_no = change.get('stock_no')
            symbol = change.get('symbol')
            quantity_delta = change.get('quantity_delta', 0)
            quantity = change.get('quantity')
            price = change.get('price')
            
            # 신규 종목 추가
            if symbol and not stock_no:
                stock, error = stock_service.get_or_create_stock(symbol)
                if error:
                    continue  # 종목을 찾을 수 없으면 스킵
                stock_no = stock['stock_no']
                
                if stock_no not in simulated_stocks:
                    simulated_stocks[stock_no] = {
                        'stock_no': stock_no,
                        'symbol': stock['symbol'],
                        'name': stock['name'],
                        'quantity': quantity or 0,
                        'avg_price': price or stock.get('current_price', 0),
                        'current_price': stock.get('current_price', price or 0),
                        'sector_name': stock.get('sector_name', '기타')
                    }
                    continue
            
            # 기존 종목 수량 변경
            if stock_no in simulated_stocks:
                if quantity_delta:
                    simulated_stocks[stock_no]['quantity'] += quantity_delta
                elif quantity is not None:
                    simulated_stocks[stock_no]['quantity'] = quantity
                
                # 수량이 0 이하면 제거
                if simulated_stocks[stock_no]['quantity'] <= 0:
                    del simulated_stocks[stock_no]
        
        # 4. 시뮬레이션 결과 계산 (after)
        after_summary = _calculate_simulated_summary(list(simulated_stocks.values()))
        after_risk = _calculate_simulated_risk(list(simulated_stocks.values()))
        
        # 5. 변화량 계산 (diff)
        diff = {
            "total_invested": after_summary['total_invested'] - before_summary['total_invested'],
            "total_value": after_summary['total_value'] - before_summary['total_value'],
            "total_return": round(after_summary['total_return'] - before_summary['total_return'], 2),
            "portfolio_volatility": round(after_risk['portfolio_volatility'] - before_risk['portfolio_volatility'], 2),
            "sharpe_ratio": round(after_risk['sharpe_ratio'] - before_risk['sharpe_ratio'], 2),
            "stock_count": len(simulated_stocks) - len(current_stocks)
        }
        
        return {
            "before": {
                "summary": before_summary,
                "risk": before_risk
            },
            "after": {
                "summary": after_summary,
                "risk": after_risk
            },
            "diff": diff,
            "simulated_stocks": list(simulated_stocks.values())
        }, None
    except Exception as e:
        return None, str(e)


def _calculate_simulated_summary(stocks):
    """시뮬레이션용 요약 계산"""
    if not stocks:
        return {
            "total_invested": 0,
            "total_value": 0,
            "total_return": 0,
            "total_profit": 0
        }
    
    total_invested = 0
    total_value = 0
    
    for s in stocks:
        invested = s['quantity'] * s['avg_price']
        current_price = s.get('current_price') or s['avg_price']
        value = s['quantity'] * current_price
        
        total_invested += invested
        total_value += value
    
    total_profit = total_value - total_invested
    total_return = (total_profit / total_invested * 100) if total_invested > 0 else 0
    
    return {
        "total_invested": total_invested,
        "total_value": total_value,
        "total_return": round(total_return, 2),
        "total_profit": total_profit
    }


def _calculate_simulated_risk(stocks):
    """시뮬레이션용 리스크 계산 (간소화 버전)"""
    if not stocks:
        return {
            "portfolio_volatility": 0,
            "sharpe_ratio": 0
        }
    
    # TODO: 실제 가격 히스토리 기반 계산으로 개선
    # 현재는 DB에서 가져온 종목별 변동성의 가중평균으로 계산
    
    total_value = sum(s['quantity'] * (s.get('current_price') or s['avg_price']) for s in stocks)
    
    weighted_vol = 0
    weighted_sharpe = 0
    
    for s in stocks:
        current_price = s.get('current_price') or s['avg_price']
        value = s['quantity'] * current_price
        weight = value / total_value if total_value > 0 else 0
        
        # 종목별 변동성 (DB에서 조회하거나 기본값 사용)
        vol = s.get('volatility', 20)  # 기본 20%
        sharpe = s.get('sharpe_ratio', 0.5)  # 기본 0.5
        
        weighted_vol += weight * vol
        weighted_sharpe += weight * sharpe
    
    return {
        "portfolio_volatility": round(weighted_vol, 2),
        "sharpe_ratio": round(weighted_sharpe, 2)
    }
