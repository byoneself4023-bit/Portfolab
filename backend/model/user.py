# -*- coding: utf-8 -*-
from db import get_connection


def find_by_email(email):
    """이메일로 사용자 조회"""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = "SELECT * FROM user WHERE email = %s AND is_deleted = 0"
            cursor.execute(sql, (email,))
            return cursor.fetchone()
    finally:
        conn.close()


def find_by_no(user_no):
    """user_no로 사용자 조회"""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = "SELECT * FROM user WHERE user_no = %s AND is_deleted = 0"
            cursor.execute(sql, (user_no,))
            return cursor.fetchone()
    finally:
        conn.close()


def create_user(email, password, nickname, role_no=1):
    """사용자 생성"""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO user (email, password, nickname, role_no)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql, (email, password, nickname, role_no))
            conn.commit()
            return cursor.lastrowid
    except Exception:
        return None
    finally:
        conn.close()


def update_user(user_no, data):
    """사용자 정보 수정"""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            set_clause = ", ".join([f"{k} = %s" for k in data.keys()])
            sql = f"UPDATE user SET {set_clause} WHERE user_no = %s"
            values = list(data.values()) + [user_no]
            cursor.execute(sql, values)
            conn.commit()
            return cursor.rowcount > 0
    finally:
        conn.close()


def soft_delete(user_no):
    """사용자 소프트 삭제"""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = "UPDATE user SET is_deleted = 1 WHERE user_no = %s"
            cursor.execute(sql, (user_no,))
            conn.commit()
            return cursor.rowcount > 0
    finally:
        conn.close()
