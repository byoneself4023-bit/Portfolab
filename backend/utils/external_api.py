# -*- coding: utf-8 -*-
"""
한국투자증권 OpenAPI 연동
"""
import os
import requests
from datetime import datetime


class KISApi:
    """한국투자증권 API 클라이언트"""
    
    BASE_URL = "https://openapi.koreainvestment.com:9443"
    
    def __init__(self):
        self.app_key = os.getenv('KIS_APP_KEY')
        self.app_secret = os.getenv('KIS_APP_SECRET')
        self.access_token = None
        self.token_expires = None
    
    def _get_access_token(self):
        """접근 토큰 발급"""
        if self.access_token and self.token_expires and datetime.now() < self.token_expires:
            return self.access_token
        
        url = f"{self.BASE_URL}/oauth2/tokenP"
        headers = {"Content-Type": "application/json"}
        data = {
            "grant_type": "client_credentials",
            "appkey": self.app_key,
            "appsecret": self.app_secret
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=10)
            response.raise_for_status()
            result = response.json()
            
            self.access_token = result.get('access_token')
            # 토큰 유효기간 설정 (약 24시간이지만 안전하게 23시간)
            from datetime import timedelta
            self.token_expires = datetime.now() + timedelta(hours=23)
            
            return self.access_token
        except Exception as e:
            print(f"토큰 발급 오류: {e}")
            return None
    
    def _get_headers(self, tr_id):
        """API 요청 헤더 생성"""
        token = self._get_access_token()
        if not token:
            return None
        
        return {
            "Content-Type": "application/json; charset=utf-8",
            "authorization": f"Bearer {token}",
            "appkey": self.app_key,
            "appsecret": self.app_secret,
            "tr_id": tr_id
        }
    
    def get_stock_price(self, symbol):
        """
        주식 현재가 조회
        
        Args:
            symbol: 종목코드 (예: "005930")
        
        Returns:
            {
                "symbol": "005930",
                "current_price": 70000,
                "change": 1000,
                "change_rate": 1.45,
                "volume": 12345678
            }
        """
        headers = self._get_headers("FHKST01010100")  # 주식현재가 조회
        if not headers:
            return None
        
        url = f"{self.BASE_URL}/uapi/domestic-stock/v1/quotations/inquire-price"
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",  # J: 주식, ETF, ETN
            "FID_INPUT_ISCD": symbol
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            result = response.json()
            
            if result.get('rt_cd') != '0':
                return None
            
            output = result.get('output', {})
            
            return {
                "symbol": symbol,
                "current_price": int(output.get('stck_prpr', 0)),
                "change": int(output.get('prdy_vrss', 0)),
                "change_rate": float(output.get('prdy_ctrt', 0)),
                "volume": int(output.get('acml_vol', 0)),
                "high": int(output.get('stck_hgpr', 0)),
                "low": int(output.get('stck_lwpr', 0)),
                "open": int(output.get('stck_oprc', 0))
            }
        except Exception as e:
            print(f"시세 조회 오류: {e}")
            return None
    
    def get_stock_info(self, symbol):
        """
        종목 기본 정보 조회
        
        Returns:
            {
                "symbol": "005930",
                "name": "삼성전자",
                "market": "KOSPI",
                "current_price": 70000
            }
        """
        # 현재가 조회로 기본 정보 획득
        price_data = self.get_stock_price(symbol)
        if not price_data:
            return None
        
        # 종목명은 별도 API 필요 - 일단 현재가 정보만 반환
        # TODO: 종목 마스터 조회 API 연동
        return {
            "symbol": symbol,
            "name": f"종목_{symbol}",  # 실제로는 API에서 조회 필요
            "market": "KOSPI",  # 기본값
            "current_price": price_data['current_price']
        }
    
    def get_price_history(self, symbol, period="D", count=90):
        """
        일별 시세 조회
        
        Args:
            symbol: 종목코드
            period: "D"(일), "W"(주), "M"(월)
            count: 조회 개수
        
        Returns:
            [{"date": "2024-01-15", "close_price": 70000, ...}, ...]
        """
        headers = self._get_headers("FHKST01010400")  # 일별 시세
        if not headers:
            return None
        
        url = f"{self.BASE_URL}/uapi/domestic-stock/v1/quotations/inquire-daily-price"
        
        # 조회 기간 설정
        from datetime import timedelta
        end_date = datetime.now().strftime("%Y%m%d")
        start_date = (datetime.now() - timedelta(days=count + 30)).strftime("%Y%m%d")
        
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": symbol,
            "FID_PERIOD_DIV_CODE": period,
            "FID_ORG_ADJ_PRC": "0",  # 수정주가 반영
            "FID_INPUT_DATE_1": start_date,
            "FID_INPUT_DATE_2": end_date
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            result = response.json()
            
            if result.get('rt_cd') != '0':
                return None
            
            output = result.get('output', [])
            
            history = []
            for item in output[:count]:
                history.append({
                    "date": f"{item['stck_bsop_date'][:4]}-{item['stck_bsop_date'][4:6]}-{item['stck_bsop_date'][6:]}",
                    "close_price": int(item.get('stck_clpr', 0)),
                    "open_price": int(item.get('stck_oprc', 0)),
                    "high_price": int(item.get('stck_hgpr', 0)),
                    "low_price": int(item.get('stck_lwpr', 0)),
                    "volume": int(item.get('acml_vol', 0))
                })
            
            # 날짜 오름차순 정렬
            history.reverse()
            return history
        except Exception as e:
            print(f"히스토리 조회 오류: {e}")
            return None


# 싱글톤 인스턴스
kis_api = KISApi()
