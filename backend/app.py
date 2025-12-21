# -*- coding: utf-8 -*-
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os

from db import check_db_connection

# 환경변수 로드
load_dotenv()

# Flask 앱 생성
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# JWT 설정
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'default-secret-key')


# ======================
# Blueprint 등록
# ======================
from routes.auth import auth_bp
from routes.stock import stock_bp
from routes.portfolio import portfolio_bp
from routes.portfolio_stock import portfolio_stock_bp
from routes.analysis import analysis_bp
from routes.simulation import simulation_bp
from routes.ai import ai_bp

app.register_blueprint(auth_bp)
app.register_blueprint(stock_bp)
app.register_blueprint(portfolio_bp)
app.register_blueprint(portfolio_stock_bp)
app.register_blueprint(analysis_bp)
app.register_blueprint(simulation_bp)
app.register_blueprint(ai_bp)


# ======================
# Health Check
# ======================
@app.route('/health', methods=['GET'])
def health_check():
    """서버 및 DB 상태 확인"""
    db_ok, db_info = check_db_connection()
    
    return jsonify({
        "success": True,
        "status": "healthy" if db_ok else "unhealthy",
        "database": {
            "connected": db_ok,
            "version": db_info if db_ok else None,
            "error": db_info if not db_ok else None
        },
        "service": "PortfoLab API"
    }), 200 if db_ok else 500


@app.route('/', methods=['GET'])
def index():
    """루트 경로"""
    return jsonify({
        "success": True,
        "message": "PortfoLab API Server",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "auth": "/auth/*",
            "stock": "/stock/*",
            "portfolio": "/portfolio/*",
            "analysis": "/analysis/*",
            "simulation": "/simulation/*",
            "ai": "/ai/*"
        }
    })


# ======================
# 에러 핸들러
# ======================
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "message": "요청한 리소스를 찾을 수 없습니다."
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "success": False,
        "message": "서버 내부 오류가 발생했습니다."
    }), 500


# ======================
# 실행
# ======================
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
