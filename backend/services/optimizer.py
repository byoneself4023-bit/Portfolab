# -*- coding: utf-8 -*-
import numpy as np
from scipy.optimize import minimize
from db import get_connection

def get_stock_returns(stock_no):
    """종목의 일별 수익률 조회 (전체 데이터)"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT close_price FROM price_history 
        WHERE stock_no = %s 
        ORDER BY date ASC
    ''', (stock_no,))
    
    prices = [row['close_price'] for row in cursor.fetchall()]
    conn.close()
    
    if len(prices) < 2:
        return []
    
    returns = []
    for i in range(1, len(prices)):
        r = (prices[i] - prices[i-1]) / prices[i-1]
        returns.append(r)
    
    return returns

def markowitz_optimize(portfolio_no):
    """마코위츠 최적 포트폴리오 계산"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 포트폴리오 종목 조회
    cursor.execute('''
        SELECT ps.stock_no, s.symbol, s.name, ps.quantity, s.current_price
        FROM portfolio_stock ps
        JOIN stock s ON ps.stock_no = s.stock_no
        WHERE ps.portfolio_no = %s
    ''', (portfolio_no,))
    
    stocks = cursor.fetchall()
    conn.close()
    
    if len(stocks) < 2:
        return {"error": "최소 2개 이상의 종목이 필요합니다"}
    
    # 현재 비중 계산
    total_value = sum(s['quantity'] * s['current_price'] for s in stocks)
    current_weights = [(s['quantity'] * s['current_price']) / total_value for s in stocks]
    
    # 각 종목의 수익률 데이터 수집
    stock_data = []
    for i, stock in enumerate(stocks):
        returns = get_stock_returns(stock['stock_no'])
        if len(returns) > 10:
            stock_data.append({
                "stock_no": stock['stock_no'],
                "symbol": stock['symbol'],
                "name": stock['name'],
                "returns": returns,
                "current_weight": current_weights[i]
            })
    
    if len(stock_data) < 2:
        return {"error": "수익률 데이터가 부족합니다"}
    
    # 수익률 배열 생성 (공통 기간만 사용)
    min_len = min(len(s['returns']) for s in stock_data)
    returns_matrix = np.array([s['returns'][-min_len:] for s in stock_data])
    
    # 기대수익률 및 공분산
    mean_returns = np.mean(returns_matrix, axis=1)
    cov_matrix = np.cov(returns_matrix)
    
    n = len(stock_data)
    
    # 목적함수: 변동성 최소화
    def portfolio_volatility(weights):
        return np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
    
    # 제약조건: 비중 합 = 1
    constraints = [{"type": "eq", "fun": lambda w: np.sum(w) - 1}]
    
    # 비중 범위: 0~1
    bounds = [(0, 1) for _ in range(n)]
    
    # 초기값: 동일 비중
    init_weights = [1/n] * n
    
    # 최적화 실행
    result = minimize(
        portfolio_volatility,
        init_weights,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints
    )
    
    optimal_weights = result.x
    
    # 결과 정리
    recommendations = []
    for i, stock in enumerate(stock_data):
        recommendations.append({
            "symbol": stock['symbol'],
            "name": stock['name'],
            "current_weight": round(stock['current_weight'] * 100, 1),
            "optimal_weight": round(optimal_weights[i] * 100, 1)
        })
    
    recommendations.sort(key=lambda x: x['optimal_weight'], reverse=True)
    
    return {
        "success": True,
        "data_days": min_len,
        "recommendations": recommendations,
        "expected_return": round(np.dot(optimal_weights, mean_returns) * 252 * 100, 2),
        "volatility": round(portfolio_volatility(optimal_weights) * np.sqrt(252) * 100, 2),
        "warnings": [
            "과거 상관관계가 미래에도 유지된다고 가정합니다",
            "위기 상황에서는 모든 자산이 동시에 하락할 수 있습니다",
            f"공통 데이터 기간 {min_len}일 기준으로 계산되었습니다"
        ]
    }