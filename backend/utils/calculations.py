# -*- coding: utf-8 -*-
"""
포트폴리오 분석을 위한 수학 계산 함수들
"""
import numpy as np
from typing import List, Dict


def calculate_returns(prices: List[float]) -> List[float]:
    """
    일별 수익률 계산
    
    Args:
        prices: 가격 리스트 (시간순 정렬)
    
    Returns:
        일별 수익률 리스트
    """
    if len(prices) < 2:
        return []
    
    returns = []
    for i in range(1, len(prices)):
        if prices[i-1] != 0:
            r = (prices[i] - prices[i-1]) / prices[i-1]
            returns.append(r)
    return returns


def calculate_volatility(returns: List[float], annualize: bool = True) -> float:
    """
    변동성 계산 (표준편차)
    
    Args:
        returns: 수익률 리스트
        annualize: 연율화 여부 (기본 True)
    
    Returns:
        변동성 (연율화된 경우 연간 기준)
    """
    if not returns:
        return 0.0
    
    std = np.std(returns, ddof=1)  # 표본 표준편차
    
    if annualize:
        # 연간 거래일 약 252일 기준
        return std * np.sqrt(252)
    return std


def calculate_sharpe_ratio(returns: List[float], risk_free_rate: float = 0.035) -> float:
    """
    샤프 비율 계산
    
    Sharpe Ratio = (평균 수익률 - 무위험 수익률) / 표준편차
    
    Args:
        returns: 일별 수익률 리스트
        risk_free_rate: 연간 무위험 수익률 (기본 3.5%)
    
    Returns:
        샤프 비율
    """
    if not returns:
        return 0.0
    
    # 연율화된 평균 수익률
    avg_return = np.mean(returns) * 252
    
    # 연율화된 변동성
    volatility = calculate_volatility(returns, annualize=True)
    
    if volatility == 0:
        return 0.0
    
    return (avg_return - risk_free_rate) / volatility


def calculate_correlation_matrix(returns_dict: Dict[str, List[float]]) -> Dict:
    """
    종목 간 상관관계 매트릭스 계산
    
    Args:
        returns_dict: {종목심볼: 수익률 리스트} 딕셔너리
    
    Returns:
        {"symbols": [...], "matrix": [[...]]}
    """
    symbols = list(returns_dict.keys())
    n = len(symbols)
    
    if n < 2:
        return {"symbols": symbols, "matrix": [[1.0]] if n == 1 else []}
    
    # 수익률 길이 맞추기 (가장 짧은 것 기준)
    min_length = min(len(returns_dict[s]) for s in symbols)
    
    if min_length < 2:
        return {"symbols": symbols, "matrix": []}
    
    # 상관관계 행렬 계산
    matrix = np.zeros((n, n))
    
    for i in range(n):
        for j in range(n):
            if i == j:
                matrix[i][j] = 1.0
            elif i < j:
                # numpy corrcoef 사용
                r1 = returns_dict[symbols[i]][:min_length]
                r2 = returns_dict[symbols[j]][:min_length]
                
                corr = np.corrcoef(r1, r2)[0, 1]
                
                # NaN 처리
                if np.isnan(corr):
                    corr = 0.0
                
                matrix[i][j] = round(corr, 4)
                matrix[j][i] = round(corr, 4)  # 대칭
    
    return {
        "symbols": symbols,
        "matrix": matrix.tolist()
    }


def calculate_covariance_matrix(returns_dict: Dict[str, List[float]]) -> np.ndarray:
    """
    공분산 행렬 계산
    
    Args:
        returns_dict: {종목심볼: 수익률 리스트} 딕셔너리
    
    Returns:
        공분산 행렬 (numpy array)
    """
    symbols = list(returns_dict.keys())
    
    if len(symbols) < 1:
        return np.array([])
    
    # 수익률 길이 맞추기
    min_length = min(len(returns_dict[s]) for s in symbols)
    
    # 데이터 배열 생성
    data = np.array([returns_dict[s][:min_length] for s in symbols])
    
    # 공분산 행렬 계산 및 연율화
    cov_matrix = np.cov(data) * 252
    
    return cov_matrix


def calculate_portfolio_volatility(weights: List[float], cov_matrix: np.ndarray) -> float:
    """
    포트폴리오 전체 변동성 계산 (공분산 기반)
    
    σ_p = sqrt(w^T * Σ * w)
    
    Args:
        weights: 종목별 비중 리스트
        cov_matrix: 공분산 행렬
    
    Returns:
        포트폴리오 변동성
    """
    weights = np.array(weights)
    
    if len(weights) != len(cov_matrix):
        return 0.0
    
    variance = np.dot(weights.T, np.dot(cov_matrix, weights))
    return np.sqrt(variance)


def calculate_max_drawdown(prices: List[float]) -> float:
    """
    최대 낙폭(MDD) 계산
    
    Args:
        prices: 가격 리스트
    
    Returns:
        최대 낙폭 (%)
    """
    if len(prices) < 2:
        return 0.0
    
    prices = np.array(prices)
    cummax = np.maximum.accumulate(prices)
    drawdown = (prices - cummax) / cummax
    
    return abs(min(drawdown)) * 100


def calculate_beta(stock_returns: List[float], market_returns: List[float]) -> float:
    """
    베타 계산 (시장 대비 민감도)
    
    Beta = Cov(stock, market) / Var(market)
    
    Args:
        stock_returns: 종목 수익률
        market_returns: 시장(벤치마크) 수익률
    
    Returns:
        베타 값
    """
    if len(stock_returns) < 2 or len(market_returns) < 2:
        return 1.0
    
    # 길이 맞추기
    min_length = min(len(stock_returns), len(market_returns))
    stock_returns = stock_returns[:min_length]
    market_returns = market_returns[:min_length]
    
    covariance = np.cov(stock_returns, market_returns)[0, 1]
    market_variance = np.var(market_returns, ddof=1)
    
    if market_variance == 0:
        return 1.0
    
    return covariance / market_variance
