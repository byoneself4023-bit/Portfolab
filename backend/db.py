# -*- coding: utf-8 -*-
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()


def connect_to_mysql(host=None, port=None, user=None, password=None, database=None):
    """MariaDB 연결"""
    return pymysql.connect(
        host=host or os.getenv('DB_HOST', 'localhost'),
        port=port or int(os.getenv('DB_PORT', 3306)),
        user=user or os.getenv('DB_USER', 'root'),
        password=password or os.getenv('DB_PASSWORD', ''),
        database=database or os.getenv('DB_DATABASE', 'portfolab'),
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )


def get_connection():
    """기본 DB 연결 반환"""
    return connect_to_mysql()


def check_db_connection():
    """DB 연결 상태 확인"""
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
        conn.close()
        return True, version
    except Exception as e:
        return False, str(e)
