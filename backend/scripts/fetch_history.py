# -*- coding: utf-8 -*-
"""
Yahoo Finance에서 5년치 데이터 가져와서 price_history 테이블에 저장
"""
import sys
sys.path.append('/Users/kuka/portfolab/backend')

import yfinance as yf
from db import get_connection


def get_all_stocks():
    """DB에 등록된 모든 종목 조회"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT stock_no, symbol, name FROM stock')
    stocks = cursor.fetchall()
    conn.close()
    return stocks


def fetch_and_save(stock_no, symbol, name):
    """Yahoo Finance에서 데이터 가져와서 저장"""
    yahoo_symbol = f"{symbol}.KS"
    
    print(f"[{name}] {yahoo_symbol} 데이터 조회 중...")
    
    try:
        df = yf.download(yahoo_symbol, period='5y', progress=False)
        
        if df.empty:
            yahoo_symbol = f"{symbol}.KQ"
            df = yf.download(yahoo_symbol, period='5y', progress=False)
        
        if df.empty:
            print(f"  ❌ 데이터 없음")
            return 0
        
        conn = get_connection()
        cursor = conn.cursor()
        
        # 기존 데이터 삭제
        cursor.execute('DELETE FROM price_history WHERE stock_no = %s', (stock_no,))
        
        # 새 데이터 삽입
        count = 0
        for date, row in df.iterrows():
            try:
                close = int(row['Close'].iloc[0]) if hasattr(row['Close'], 'iloc') else int(row['Close'])
                open_p = int(row['Open'].iloc[0]) if hasattr(row['Open'], 'iloc') else int(row['Open'])
                high = int(row['High'].iloc[0]) if hasattr(row['High'], 'iloc') else int(row['High'])
                low = int(row['Low'].iloc[0]) if hasattr(row['Low'], 'iloc') else int(row['Low'])
                volume = int(row['Volume'].iloc[0]) if hasattr(row['Volume'], 'iloc') else int(row['Volume'])
                
                cursor.execute('''
                    INSERT INTO price_history (stock_no, date, close_price, open_price, high_price, low_price, volume)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                ''', (stock_no, date.strftime('%Y-%m-%d'), close, open_p, high, low, volume))
                count += 1
            except Exception as e:
                continue
        
        conn.commit()
        conn.close()
        print(f"  ✅ {count}일치 저장 완료")
        return count
        
    except Exception as e:
        print(f"  ❌ 오류: {e}")
        return 0


def main():
    stocks = get_all_stocks()
    print(f"총 {len(stocks)}개 종목 처리 시작\n")
    
    total = 0
    for stock in stocks:
        count = fetch_and_save(stock['stock_no'], stock['symbol'], stock['name'])
        total += count
    
    print(f"\n완료! 총 {total}개 레코드 저장됨")


if __name__ == '__main__':
    main()