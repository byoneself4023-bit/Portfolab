# -*- coding: utf-8 -*-
from model import portfolio_stock as ps_model
from model import stock as stock_model
from utils.calculations import (
    calculate_returns,
    calculate_volatility,
    calculate_sharpe_ratio,
    calculate_correlation_matrix,
    calculate_portfolio_volatility
)


def get_portfolio_summary(portfolio_no):
    """
    기본 지표 계산
    - 총 투자금액
    - 총 평가금액
    - 총 수익률
    - 총 손익
    """
    try:
        stocks = ps_model.find_by_portfolio_no_with_stock_info(portfolio_no)
        
        if not stocks:
            return {
                "total_invested": 0,
                "total_value": 0,
                "total_return": 0,
                "total_profit": 0,
                "stocks": []
            }, None
        
        total_invested = 0
        total_value = 0
        stock_summaries = []
        
        for s in stocks:
            invested = s['quantity'] * s['avg_price']
            current_price = s.get('current_price') or s['avg_price']  # 현재가 없으면 매수가 사용
            value = s['quantity'] * current_price
            profit = value - invested
            return_pct = (profit / invested * 100) if invested > 0 else 0
            
            total_invested += invested
            total_value += value
            
            stock_summaries.append({
                "stock_no": s['stock_no'],
                "symbol": s['symbol'],
                "name": s['name'],
                "quantity": s['quantity'],
                "avg_price": s['avg_price'],
                "current_price": current_price,
                "invested": invested,
                "value": value,
                "profit": profit,
                "return_pct": round(return_pct, 2),
                "weight": 0  # 나중에 계산
            })
        
        # 비중 계산
        for s in stock_summaries:
            s['weight'] = round(s['value'] / total_value * 100, 2) if total_value > 0 else 0
        
        total_profit = total_value - total_invested
        total_return = (total_profit / total_invested * 100) if total_invested > 0 else 0
        
        return {
            "total_invested": total_invested,
            "total_value": total_value,
            "total_return": round(total_return, 2),
            "total_profit": total_profit,
            "stocks": stock_summaries
        }, None
    except Exception as e:
        return None, str(e)


def get_risk_metrics(portfolio_no):
    """
    리스크 지표 계산
    - 포트폴리오 변동성 (연율화)
    - 샤프 비율
    - 개별 종목 변동성
    """
    try:
        stocks = ps_model.find_by_portfolio_no_with_stock_info(portfolio_no)
        
        if not stocks:
            return {
                "portfolio_volatility": 0,
                "sharpe_ratio": 0,
                "stock_volatilities": []
            }, None
        
        # 각 종목의 가격 히스토리 조회 및 수익률 계산
        returns_dict = {}
        weights = []
        stock_volatilities = []
        
        total_value = sum(s['quantity'] * (s.get('current_price') or s['avg_price']) for s in stocks)
        
        for s in stocks:
            history = stock_model.get_price_history(s['stock_no'], days=90)
            
            if history and len(history) > 1:
                prices = [h['close_price'] for h in history]
                returns = calculate_returns(prices)
                returns_dict[s['symbol']] = returns
                
                vol = calculate_volatility(returns)
                sharpe = calculate_sharpe_ratio(returns)
            else:
                vol = 0
                sharpe = 0
            
            current_price = s.get('current_price') or s['avg_price']
            value = s['quantity'] * current_price
            weight = value / total_value if total_value > 0 else 0
            weights.append(weight)
            
            stock_volatilities.append({
                "stock_no": s['stock_no'],
                "symbol": s['symbol'],
                "name": s['name'],
                "volatility": round(vol * 100, 2),  # 퍼센트로 변환
                "sharpe_ratio": round(sharpe, 2),
                "weight": round(weight * 100, 2)
            })
        
        # 포트폴리오 전체 변동성 계산 (단순 가중평균 - 상관관계 미고려 버전)
        # TODO: 공분산 행렬 기반 정확한 계산으로 개선
        portfolio_vol = sum(w * sv['volatility'] / 100 for w, sv in zip(weights, stock_volatilities))
        
        # 포트폴리오 샤프비율 (단순 가중평균)
        portfolio_sharpe = sum(w * sv['sharpe_ratio'] for w, sv in zip(weights, stock_volatilities))
        
        return {
            "portfolio_volatility": round(portfolio_vol * 100, 2),
            "sharpe_ratio": round(portfolio_sharpe, 2),
            "risk_free_rate": 3.5,  # 무위험 수익률 (한국 기준)
            "stock_volatilities": stock_volatilities
        }, None
    except Exception as e:
        return None, str(e)


def get_correlation_matrix(portfolio_no):
    """상관관계 매트릭스 계산"""
    try:
        stocks = ps_model.find_by_portfolio_no_with_stock_info(portfolio_no)
        
        if not stocks or len(stocks) < 2:
            return {
                "message": "상관관계 분석을 위해서는 최소 2개 이상의 종목이 필요합니다.",
                "symbols": [],
                "matrix": []
            }, None
        
        # 각 종목의 수익률 계산
        returns_dict = {}
        symbols = []
        
        for s in stocks:
            history = stock_model.get_price_history(s['stock_no'], days=90)
            
            if history and len(history) > 1:
                prices = [h['close_price'] for h in history]
                returns = calculate_returns(prices)
                returns_dict[s['symbol']] = returns
                symbols.append(s['symbol'])
        
        if len(symbols) < 2:
            return {
                "message": "가격 데이터가 충분한 종목이 2개 미만입니다.",
                "symbols": [],
                "matrix": []
            }, None
        
        # 상관관계 매트릭스 계산
        correlation = calculate_correlation_matrix(returns_dict)
        
        return correlation, None
    except Exception as e:
        return None, str(e)


def get_sector_distribution(portfolio_no):
    """섹터 분포 계산"""
    try:
        stocks = ps_model.find_by_portfolio_no_with_stock_info(portfolio_no)
        
        if not stocks:
            return {"sectors": []}, None
        
        sector_values = {}
        total_value = 0
        
        for s in stocks:
            current_price = s.get('current_price') or s['avg_price']
            value = s['quantity'] * current_price
            total_value += value
            
            sector = s.get('sector_name') or '기타'
            sector_values[sector] = sector_values.get(sector, 0) + value
        
        sectors = []
        for sector, value in sector_values.items():
            sectors.append({
                "sector": sector,
                "value": value,
                "weight": round(value / total_value * 100, 2) if total_value > 0 else 0
            })
        
        # 비중 순으로 정렬
        sectors.sort(key=lambda x: x['weight'], reverse=True)
        
        return {
            "total_value": total_value,
            "sectors": sectors
        }, None
    except Exception as e:
        return None, str(e)
