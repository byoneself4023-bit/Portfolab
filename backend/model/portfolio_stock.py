# -*- coding: utf-8 -*-
from db import get_connection


def insert(portfolio_no, stock_no, quantity, avg_price):
    """포트폴리오에 종목 추가"""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO portfolio_stock (portfolio_no, stock_no, quantity, avg_price)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql, (portfolio_no, stock_no, quantity, avg_price))
            conn.commit()
            return True
    except Exception:
        return False
    finally:
        conn.close()


def find_by_portfolio_no(portfolio_no):
    """포트폴리오의 종목 목록 (기본)"""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT * FROM portfolio_stock
                WHERE portfolio_no = %s
            """
            cursor.execute(sql, (portfolio_no,))
            return cursor.fetchall()
    finally:
        conn.close()


def find_by_portfolio_no_with_stock_info(portfolio_no):
    """포트폴리오의 종목 목록 (종목 정보 포함)"""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT 
                    ps.*,
                    s.symbol,
                    s.name,
                    s.market,
                    s.current_price,
                    sec.name as sector_name
                FROM portfolio_stock ps
                JOIN stock s ON ps.stock_no = s.stock_no
                LEFT JOIN sector sec ON s.sector_no = sec.sector_no
                WHERE ps.portfolio_no = %s
            """
            cursor.execute(sql, (portfolio_no,))
            return cursor.fetchall()
    finally:
        conn.close()


def find_one(portfolio_no, stock_no):
    """특정 종목 조회"""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT 
                    ps.*,
                    s.symbol,
                    s.name,
                    s.current_price
                FROM portfolio_stock ps
                JOIN stock s ON ps.stock_no = s.stock_no
                WHERE ps.portfolio_no = %s AND ps.stock_no = %s
            """
            cursor.execute(sql, (portfolio_no, stock_no))
            return cursor.fetchone()
    finally:
        conn.close()


def exists(portfolio_no, stock_no):
    """종목 존재 여부 확인"""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT 1 FROM portfolio_stock
                WHERE portfolio_no = %s AND stock_no = %s
            """
            cursor.execute(sql, (portfolio_no, stock_no))
            return cursor.fetchone() is not None
    finally:
        conn.close()


def update(portfolio_no, stock_no, data):
    """종목 정보 수정"""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            set_clause = ", ".join([f"{k} = %s" for k in data.keys()])
            sql = f"""
                UPDATE portfolio_stock 
                SET {set_clause}
                WHERE portfolio_no = %s AND stock_no = %s
            """
            values = list(data.values()) + [portfolio_no, stock_no]
            cursor.execute(sql, values)
            conn.commit()
            return cursor.rowcount > 0
    finally:
        conn.close()


def delete(portfolio_no, stock_no):
    """포트폴리오에서 종목 삭제"""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                DELETE FROM portfolio_stock
                WHERE portfolio_no = %s AND stock_no = %s
            """
            cursor.execute(sql, (portfolio_no, stock_no))
            conn.commit()
            return cursor.rowcount > 0
    finally:
        conn.close()
