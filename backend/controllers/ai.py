# -*- coding: utf-8 -*-
from flask import request, jsonify
from services import ai as ai_service
from services import analysis as analysis_service
from model import portfolio_stock as ps_model


def analyze_portfolio(portfolio_no):
    """포트폴리오 AI 분석"""
    try:
        # 포트폴리오 데이터 수집
        summary, err = analysis_service.get_portfolio_summary(portfolio_no)
        if err:
            return jsonify({"success": False, "message": err}), 400
        
        risk, err = analysis_service.get_risk_metrics(portfolio_no)
        if err:
            return jsonify({"success": False, "message": err}), 400
        
        stocks = ps_model.find_by_portfolio_no_with_stock_info(portfolio_no)
        
        portfolio_data = {
            "total_invested": summary['total_invested'],
            "total_value": summary['total_value'],
            "total_return": summary['total_return'],
            "volatility": risk['portfolio_volatility'],
            "sharpe_ratio": risk['sharpe_ratio'],
            "stocks": [
                {
                    "name": s['name'],
                    "symbol": s['symbol'],
                    "quantity": s['quantity'],
                    "avg_price": s['avg_price'],
                    "current_price": s.get('current_price', s['avg_price']),
                    "sector": s.get('sector_name', '기타')
                }
                for s in stocks
            ]
        }
        
        result, error = ai_service.analyze_portfolio(portfolio_data)
        
        if error:
            return jsonify({"success": False, "message": error}), 500
        
        return jsonify({"success": True, "data": result}), 200
        
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


def get_rebalancing(portfolio_no):
    """리밸런싱 제안"""
    try:
        target_volatility = request.args.get('target', 30, type=float)
        
        risk, err = analysis_service.get_risk_metrics(portfolio_no)
        if err:
            return jsonify({"success": False, "message": err}), 400
        
        stocks = ps_model.find_by_portfolio_no_with_stock_info(portfolio_no)
        
        portfolio_data = {
            "volatility": risk['portfolio_volatility'],
            "stocks": [
                {
                    "name": s['name'],
                    "quantity": s['quantity'],
                    "current_price": s.get('current_price', s['avg_price'])
                }
                for s in stocks
            ]
        }
        
        result, error = ai_service.get_rebalancing_suggestion(portfolio_data, target_volatility)
        
        if error:
            return jsonify({"success": False, "message": error}), 500
        
        return jsonify({"success": True, "data": result}), 200
        
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


def explain_metrics():
    """지표 설명"""
    try:
        volatility = request.args.get('volatility', 0, type=float)
        sharpe_ratio = request.args.get('sharpe', 0, type=float)
        
        result, error = ai_service.explain_metrics(volatility, sharpe_ratio)
        
        if error:
            return jsonify({"success": False, "message": error}), 500
        
        return jsonify({"success": True, "data": result}), 200
        
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500