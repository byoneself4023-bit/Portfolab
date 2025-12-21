# -*- coding: utf-8 -*-
from db import get_connection


def create(user_no, name, description=''):
    """포트폴리오 생성"""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO portfolio (user_no, name, description)
                VALUES (%s, %s, %s)
            """
            cursor.execute(sql, (user_no, name, description))
            conn.commit()
            return cursor.lastrowid
    except Exception:
        return None
    finally:
        conn.close()


def find_by_no(portfolio_no):
    """portfolio_no로 조회"""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = "SELECT * FROM portfolio WHERE portfolio_no = %s"
            cursor.execute(sql, (portfolio_no,))
            return cursor.fetchone()
    finally:
        conn.close()


def find_by_user_no(user_no):
    """사용자의 포트폴리오 목록"""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT * FROM portfolio 
                WHERE user_no = %s
                ORDER BY created_at DESC
            """
            cursor.execute(sql, (user_no,))
            return cursor.fetchall()
    finally:
        conn.close()


def update(portfolio_no, data):
    """포트폴리오 수정"""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            set_clause = ", ".join([f"{k} = %s" for k in data.keys()])
            sql = f"UPDATE portfolio SET {set_clause} WHERE portfolio_no = %s"
            values = list(data.values()) + [portfolio_no]
            cursor.execute(sql, values)
            conn.commit()
            return cursor.rowcount > 0
    finally:
        conn.close()


def delete(portfolio_no):
    """포트폴리오 삭제 (CASCADE로 portfolio_stock도 삭제됨)"""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = "DELETE FROM portfolio WHERE portfolio_no = %s"
            cursor.execute(sql, (portfolio_no,))
            conn.commit()
            return cursor.rowcount > 0
    finally:
        conn.close()
