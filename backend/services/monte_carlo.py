# -*- coding: utf-8 -*-
import numpy as np
from db import get_connection

def run_simulation(portfolio_no, years=10, simulations=1000):
    """몬테카를로 시뮬레이션 실행"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 포트폴리오 현재 가치 조회
    cursor.execute('''
        SELECT SUM(ps.quantity * s.current_price) as total_value
        FROM portfolio_stock ps
        JOIN stock s ON ps.stock_no = s.stock_no
        WHERE ps.portfolio_no = %s
    ''', (portfolio_no,))
    
    result = cursor.fetchone()
    initial_value = float(result['total_value'] or 0)
    
    if initial_value == 0:
        conn.close()
        return {"error": "포트폴리오 가치가 0입니다"}
    
    # 포트폴리오 종목 조회
    cursor.execute('''
        SELECT ps.stock_no, ps.quantity, s.current_price
        FROM portfolio_stock ps
        JOIN stock s ON ps.stock_no = s.stock_no
        WHERE ps.portfolio_no = %s
    ''', (portfolio_no,))
    
    stocks = cursor.fetchall()
    
    # 각 종목 수익률 수집 (5년치 전체 사용)
    all_returns = []
    weights = []
    
    for stock in stocks:
        weight = (stock['quantity'] * float(stock['current_price'])) / initial_value
        weights.append(weight)
        
        cursor.execute('''
            SELECT close_price FROM price_history 
            WHERE stock_no = %s 
            ORDER BY date ASC
        ''', (stock['stock_no'],))
        
        prices = [float(row['close_price']) for row in cursor.fetchall()]
        
        if len(prices) > 1:
            returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
            all_returns.append(returns)
    
    conn.close()
    
    if not all_returns:
        return {"error": "수익률 데이터가 부족합니다"}
    
    # 포트폴리오 일별 수익률 계산
    min_len = min(len(r) for r in all_returns)
    portfolio_returns = []
    
    for day in range(min_len):
        daily_return = sum(weights[i] * all_returns[i][day] for i in range(len(weights)))
        portfolio_returns.append(daily_return)
    
    # 연율화
    daily_mean = np.mean(portfolio_returns)
    daily_std = np.std(portfolio_returns)
    
    annual_return = daily_mean * 252
    annual_vol = daily_std * np.sqrt(252)
    
    # 몬테카를로 시뮬레이션
    days = years * 252
    results = []
    
    for _ in range(simulations):
        value = initial_value
        for _ in range(days):
            random_return = np.random.normal(daily_mean, daily_std)
            value *= (1 + random_return)
        results.append(value)
    
    results = np.array(results)
    
    return {
        "success": True,
        "initial_value": int(initial_value),
        "years": years,
        "simulations": simulations,
        "data_days": min_len,
        "annual_return": round(annual_return * 100, 2),
        "annual_volatility": round(annual_vol * 100, 2),
        "results": {
            "min": int(np.min(results)),
            "p10": int(np.percentile(results, 10)),
            "p25": int(np.percentile(results, 25)),
            "p50": int(np.percentile(results, 50)),
            "p75": int(np.percentile(results, 75)),
            "p90": int(np.percentile(results, 90)),
            "max": int(np.max(results)),
            "mean": int(np.mean(results))
        },
        "warnings": [
            "과거 수익률이 미래를 보장하지 않습니다",
            "시뮬레이션은 정규분포를 가정하며, 실제 시장은 극단적 사건(블랙스완)이 더 자주 발생합니다",
            f"공통 데이터 기간 {min_len}일 기준으로 계산되었습니다"
        ]
    }