# -*- coding: utf-8 -*-
from db import get_connection


def find_by_symbol(symbol):
    """종목코드로 조회"""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT s.*, sec.name as sector_name
                FROM stock s
                LEFT JOIN sector sec ON s.sector_no = sec.sector_no
                WHERE s.symbol = %s
            """
            cursor.execute(sql, (symbol,))
            return cursor.fetchone()
    finally:
        conn.close()


def find_by_no(stock_no):
    """stock_no로 조회"""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT s.*, sec.name as sector_name
                FROM stock s
                LEFT JOIN sector sec ON s.sector_no = sec.sector_no
                WHERE s.stock_no = %s
            """
            cursor.execute(sql, (stock_no,))
            return cursor.fetchone()
    finally:
        conn.close()


def search_by_name_or_symbol(query, market=None):
    """종목명 또는 종목코드로 검색"""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT s.*, sec.name as sector_name
                FROM stock s
                LEFT JOIN sector sec ON s.sector_no = sec.sector_no
                WHERE (s.name LIKE %s OR s.symbol LIKE %s)
            """
            params = [f"%{query}%", f"%{query}%"]
            
            if market:
                sql += " AND s.market = %s"
                params.append(market)
            
            sql += " LIMIT 20"
            cursor.execute(sql, params)
            return cursor.fetchall()
    finally:
        conn.close()


def create_stock(data):
    """종목 생성"""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO stock (symbol, name, market, sector_no, current_price)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                data.get('symbol'),
                data.get('name'),
                data.get('market', 'KOSPI'),
                data.get('sector_no'),
                data.get('current_price')
            ))
            conn.commit()
            return cursor.lastrowid
    except Exception:
        return None
    finally:
        conn.close()


def update_current_price(symbol, price):
    """현재가 업데이트"""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                UPDATE stock 
                SET current_price = %s, price_updated_at = NOW()
                WHERE symbol = %s
            """
            cursor.execute(sql, (price, symbol))
            conn.commit()
            return cursor.rowcount > 0
    finally:
        conn.close()


def get_price_history(stock_no, days=90):
    """가격 히스토리 조회"""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT date, close_price
                FROM price_history
                WHERE stock_no = %s
                ORDER BY date DESC
                LIMIT %s
            """
            cursor.execute(sql, (stock_no, days))
            results = cursor.fetchall()
            return list(reversed(results)) if results else []
    finally:
        conn.close()


def insert_price_history(stock_no, date, close_price):
    """가격 히스토리 추가"""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO price_history (stock_no, date, close_price)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE close_price = VALUES(close_price)
            """
            cursor.execute(sql, (stock_no, date, close_price))
            conn.commit()
            return True
    except Exception:
        return False
    finally:
        conn.close()

def get_all_stocks():
    """전체 종목 목록 조회"""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT s.*, sec.name as sector_name
                FROM stock s
                LEFT JOIN sector sec ON s.sector_no = sec.sector_no
                ORDER BY s.market, s.name
            """
            cursor.execute(sql)
            return cursor.fetchall()
    finally:
        conn.close()